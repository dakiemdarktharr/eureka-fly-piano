"""A real, frozen-connectome plant with a trainable 16-parameter motor readout.

Learning changes controller parameters only. It is not synaptic learning in a fly.
The physical keyboard and event detector are fixed across all checkpoints.
"""
import hashlib,time
import numpy as np
import mujoco as mj
from paths import PROJECT,V2,read_json
import world
world.ROOT=V2
from world import PianoWorld
import simulate
simulate.ROOT=V2
from simulate import schedule,match_events
import simulation.model as neural
neural.ROOT=PROJECT

NAMES=[f'y_bias_{x}_mm' for x in world.LEGS]+[f'z_bias_{x}_mm' for x in world.LEGS]+['anticipation_s','neural_gain','neural_mix','release_shift_s']
LOW=np.array([-.09]*6+[-.10]*6+[0,.2,0,-.04])
HIGH=np.array([.09]*6+[.10]*6+[.14,2.,1.,.02])
INITIAL=np.array([0.]*12+[.10,1.,1.,0.])

def scores():return {k:read_json(V2/f'data/{k}_score.json') for k in ['merry','pool']}

def partition(score):
 """Whole-bar chronological partitions with a bar omitted at each boundary."""
 bars=score['bars'];a=int(len(bars)*.6);b=int(len(bars)*.8)
 return {'train':[0.,bars[a-1]['end']],'validation':[bars[a+1]['start'],bars[b-1]['end']],'test':[bars[b+1]['start'],score['duration']]}

def clips_for(pieces,split,length=6,count=1,rng=None):
 result=[]
 for key,s in pieces.items():
  lo,hi=partition(s)[split]
  for i in range(count):
   start=float(rng.uniform(lo,max(lo,hi-length))) if rng is not None else lo+(max(0,hi-lo-length))*(i+.5)/count
   result.append((key,start,min(length,hi-start)))
 return result

def compact(metric):return {k:v for k,v in metric.items() if k!='matches'}

class Engine:
 def __init__(self,seed=0,dt=.0002):
  self.seed=seed;self.dt=dt;self.pieces=scores();self.w=PianoWorld(dt)
  cache=V2/'data/ik_cache.npz'
  if cache.exists():c=np.load(cache);self.errors=c['error'];self.hover=c['hover'];self.press=c['press']
  else:self.hover,self.press,self.errors=simulate.ik_table(self.w)
  self.assignments={k:schedule(s,self.errors) for k,s in self.pieces.items()}
  self.geom_count=len(self.w.scene()['geoms']);self.total_steps=0
 def rollout(self,theta,key,start,duration,record=False,cancel=None):
  theta=np.asarray(theta,float)
  if theta.shape!=(16,) or not np.isfinite(theta).all() or np.any(theta<LOW-1e-9) or np.any(theta>HIGH+1e-9):raise ValueError('Invalid controller parameters')
  w=self.w;m=w.model;d=w.data;dt=self.dt
  mj.mj_resetDataKeyframe(m,d,0);mj.mj_forward(m,d)
  # Only onsets in the interval are scored. Pre-boundary sustained notes are
  # excluded symmetrically; whole-song replays have no cropped onsets.
  target=[dict(e,start=e['start']-start,end=min(e['end']-start,duration)) for e in self.assignments[key] if start<=e['start']<start+duration and e['end']>e['start']]
  seqs=[[e for e in target if e['leg']==l] for l in range(6)];ptr=np.zeros(6,dtype=int);poses={}
  for e in target:
   leg=e['leg'];pitch=e['pitch'];pair=(leg,pitch)
   if leg<0 or pair in poses:continue
   index=pitch-21
   if np.all(theta[:12]==0):h=self.hover[leg,index];p=self.press[leg,index]
   else:
    ht=w.target(leg,pitch,.14);pt=w.target(leg,pitch,-.15+theta[6+leg]);ht[1]+=theta[leg];pt[1]+=theta[leg]
    h,_=w.inverse(leg,ht,start=self.hover[leg,index]);p,_=w.inverse(leg,pt,start=self.press[leg,index])
   poses[pair]=(h,p)
  net=neural.MotorNetwork(seed=self.seed,dt=.002)
  for _ in range(1000):amp=net.step(500,-1)
  feedback=np.zeros(6);gate=np.zeros(6);forces=np.zeros(6);contact=np.zeros(88);on=np.full(88,np.nan);off=on.copy();last_off=np.full(88,-10.);opened={};actual=[];ctrl=w.neutral_ctrl.copy();frames=[];next_frame=0.;energy=0.
  stride_neural=round(.002/dt);nsteps=round(duration/dt)
  for step in range(nsteps):
   now=step*dt
   if step%1000==0 and cancel and cancel():raise InterruptedError('Pause requested')
   if step%stride_neural==0:
    amp=net.step(500,-1,feedback);gate=(1-theta[14])+theta[14]*np.clip(8*amp*theta[13],0,1);ctrl[:]=w.neutral_ctrl
    for leg,seq in enumerate(seqs):
     while ptr[leg]<len(seq) and seq[ptr[leg]]['end']+.05<now:ptr[leg]+=1
     if ptr[leg]>=len(seq):continue
     e=seq[ptr[leg]]
     if now<e['start']-theta[12]:continue
     h,p=poses[(leg,e['pitch'])];blend=gate[leg] if e['start']<=now<max(e['start'],e['end']+theta[15]) else 0
     ctrl[w.acts[leg]]=h*(1-blend)+p*blend
   w.step(ctrl);self.total_steps+=1
   if step%stride_neural==0:
    forces[:]=0;contact[:]=0
    for (pitch,leg),force in w.contacts().items():contact[pitch-21]+=force;forces[leg]+=force
    feedback=np.clip(forces/.05,0,1)
    energy+=float(np.sum(np.abs(d.actuator_force*d.actuator_velocity)))*.002
    for idx,f in enumerate(contact):
     pitch=idx+21
     if pitch not in opened:
      if f>=.003:
       if np.isnan(on[idx]):on[idx]=now
       if now-on[idx]>=.016 and now-last_off[idx]>=.04:
        event=dict(id=len(actual),pitch=pitch,start=round(float(on[idx]),6),end=None,peak_force_uN=float(f));actual.append(event);opened[pitch]=event;off[idx]=np.nan
      else:on[idx]=np.nan
     else:
      event=opened[pitch];event['peak_force_uN']=max(event['peak_force_uN'],float(f))
      if f<.0015:
       if np.isnan(off[idx]):off[idx]=now
       if now-off[idx]>=.024:event['end']=round(float(off[idx]),6);del opened[pitch];last_off[idx]=now;on[idx]=np.nan
      else:off[idx]=np.nan
   if record and now+dt/2>=next_frame:
    frames.append(np.concatenate([w.pose().ravel(),d.qpos[w.key_qids],net.r[net.dn],net.r[net.cpg],amp,forces,gate]).astype('<f4'));next_frame+=1/24
  for e in opened.values():e['end']=duration
  metrics=[match_events(target,actual,t) for t in [.025,.05,.1,.15,.25]]
  matched=metrics[2]['matches'];by_target={e['id']:e for e in target};by_actual={e['id']:e for e in actual};ious=[]
  for tid,aid,_ in matched:
   a=by_target[tid];b=by_actual[aid];intersection=max(0,min(a['end'],b['end'])-max(a['start'],b['start']));union=max(a['end'],b['end'])-min(a['start'],b['start']);ious.append(intersection/union if union else 0.)
  result={'piece':key,'clip_start_s':start,'duration':duration,'metrics':metrics,'actual':actual,'notes':target,'actuator_work_uN_mm':energy,'matched_duration_iou':float(np.mean(ious)) if ious else None,'solver_warnings':int(np.sum(d.warning.number)),'physics_steps':nsteps}
  if record:
   g=self.geom_count;array=np.stack(frames);result.update(variant='trained',seed=self.seed,fps=24,frame_count=len(array),geom_count=g,stride=g*12+126,layout={'pose':[0,g*12],'key_displacement':[g*12,88],'DN':[g*12+88,2],'CPG':[g*12+90,18],'MN':[g*12+108,6],'contact_force':[g*12+114,6],'gate':[g*12+120,6]},dt=dt,neural_dt=.002,mujoCo_warnings=result['solver_warnings'],parameters=theta.tolist(),parameter_names=NAMES,controller='CEM-trained engineered readout; frozen connectome; privileged score-to-IK retained',dtype='little-endian float32');return result,array
  return result
 def evaluate(self,theta,clips,cancel=None):
  all_results=[self.rollout(theta,*clip,cancel=cancel) for clip in clips];out={}
  for key in self.pieces:
   rs=[r for r in all_results if r['piece']==key];ms=[r['metrics'][2] for r in rs];tp=sum(m['matched'] for m in ms);nt=sum(m['target_notes'] for m in ms);na=sum(m['actual_notes'] for m in ms);p=tp/na if na else 0;r=tp/nt if nt else 0
   out[key]={'precision':p,'recall':r,'f1':2*p*r/(p+r) if p+r else 0.,'matched':tp,'target_notes':nt,'actual_notes':na,'missed':nt-tp,'extra':na-tp,'solver_warnings':sum(r['solver_warnings'] for r in rs)}
  out['macro_f1']=float(np.mean([out[k]['f1'] for k in self.pieces]));out['clips']=[list(c) for c in clips];out['physics_steps']=sum(r['physics_steps'] for r in all_results)
  return out
