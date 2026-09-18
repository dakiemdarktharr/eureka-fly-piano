"""Offline dynamic replay; pitch goals stay explicitly outside the neural graph."""
from pathlib import Path
import sys,json,time,hashlib,argparse
import numpy as np
from scipy.optimize import linear_sum_assignment
from world import PianoWorld,ROOT,LEGS,KEY_MIN,KEY_MAX
sys.path.insert(0,str(ROOT.parent))
from simulation.model import MotorNetwork

def ik_table(world):
 path=ROOT/'data/ik_cache.npz'
 if path.exists():
  v=np.load(path);return v['hover'],v['press'],v['error']
 hover=np.empty((6,88,7));press=hover.copy();error=np.empty((6,88))
 for leg in range(6):
  for pitch in range(21,109):
   hover[leg,pitch-21],_=world.inverse(leg,world.target(leg,pitch,.14))
   press[leg,pitch-21],error[leg,pitch-21]=world.inverse(leg,world.target(leg,pitch,-.15))
 np.savez(path,hover=hover,press=press,error=error)
 return hover,press,error

def schedule(piece,errors):
 notes=[dict(e,leg=-1,reason='unassigned') for e in piece['notes']]
 busy=np.zeros(6);lastpitch=np.array([83,45,90,38,83,45]);groups={}
 for e in notes:groups.setdefault(e['start'],[]).append(e)
 for onset,group in sorted(groups.items()):
  valid=[e for e in group if 21<=e['pitch']<=108 and e['end']>e['start']]
  available=np.flatnonzero(busy<=onset+.00001)
  if not len(available):
   for e in valid:e['reason']='all_legs_occupied'
   continue
  if not valid:continue
  cost=np.array([[errors[l,e['pitch']-21]*100+abs(lastpitch[l]-e['pitch'])*.004 for l in available] for e in valid])
  rows,cols=linear_sum_assignment(cost)
  for r,c in zip(rows,cols):
   e=valid[r];leg=int(available[c]);e['leg']=leg;e['ik_error_mm']=float(errors[leg,e['pitch']-21]);e['reason']='assigned' if e['ik_error_mm']<.05 else 'assigned_but_kinematically_infeasible'
   busy[leg]=e['end']+.025;lastpitch[leg]=e['pitch']
  for e in valid:
   if e['leg']<0:e['reason']='simultaneous_capacity_limit'
 return notes

def match_events(targets,actual,tolerance=.1):
 """Maximum-cardinality one-to-one onset matching; ties minimize timing error."""
 matches=[]
 for pitch in range(21,109):
  target=[e for e in targets if e['pitch']==pitch and e['end']>e['start']]
  observed=[e for e in actual if e['pitch']==pitch]
  if not target or not observed:continue
  delta=np.abs(np.array([e['start'] for e in target])[:,None]-np.array([e['start'] for e in observed])[None,:])
  # Unmatched dummy cost dominates all admissible aggregate differences.
  penalty=(len(target)+len(observed)+1)*(tolerance+1)
  cost=np.concatenate([np.where(delta<=tolerance,delta,penalty*2),np.full((len(target),len(target)),penalty)],axis=1)
  rr,cc=linear_sum_assignment(cost)
  for r,c in zip(rr,cc):
   if c<len(observed) and delta[r,c]<=tolerance:matches.append((target[r]['id'],observed[c]['id'],observed[c]['start']-target[r]['start']))
 nt=sum(e['end']>e['start'] for e in targets);na=len(actual);tp=len(matches);p=tp/na if na else 0;r=tp/nt if nt else 0
 return dict(tolerance_s=tolerance,target_notes=nt,actual_notes=na,matched=tp,precision=p,recall=r,f1=2*p*r/(p+r) if p+r else 0,missed=nt-tp,extra=na-tp,conditional_mae_s=float(np.mean([abs(v[2]) for v in matches])) if matches else None,signed_delay_s=float(np.mean([v[2] for v in matches])) if matches else None,matches=matches)

def run(key,variant='full',duration=None,dt=.0002,seed=0,save=True):
 started=time.perf_counter();piece=json.loads((ROOT/f'data/{key}_score.json').read_text(encoding='utf8'));w=PianoWorld(dt)
 hover,press,errors=ik_table(w);notes=schedule(piece,errors)
 neural_dt=.002;net=MotorNetwork(seed=seed,variant=variant if variant not in ['constant','leg_permuted'] else 'full',dt=neural_dt)
 for _ in range(1000):amp=net.step(500,-1)
 total=duration if duration is not None else piece['duration']+1
 fps=24;frames=[];actual=[];open_notes={};last_off=np.full(88,-10.);on_since=np.full(88,np.nan);off_since=np.full(88,np.nan);contact_sum=np.zeros(88);forces=np.zeros(6);ptr=np.zeros(6,dtype=int)
 legnotes=[[e for e in notes if e['leg']==leg] for leg in range(6)];ctrl=w.neutral_ctrl.copy();gate=np.zeros(6);feedback=np.zeros(6)
 neural_every=round(neural_dt/dt);next_frame=0.;geom_count=len(w.scene()['geoms']);warnings=0
 for step in range(round(total/dt)):
  now=step*dt
  if step%neural_every==0:
   amp=net.step(500,-1,feedback=feedback)
   gate=np.clip(amp*8,0,1)
   if variant=='constant':gate[:]=1
   if variant=='leg_permuted':gate=gate[np.array([3,4,5,0,1,2])]
   ctrl[:]=w.neutral_ctrl
   for leg,seq in enumerate(legnotes):
    while ptr[leg]<len(seq) and seq[ptr[leg]]['end']+.05<now:ptr[leg]+=1
    if ptr[leg]>=len(seq):continue
    e=seq[ptr[leg]];pitch=e['pitch']-21
    if now<e['start']-.1:continue
    blend=gate[leg] if e['start']<=now<e['end'] else 0
    ctrl[w.acts[leg]]=hover[leg,pitch]*(1-blend)+press[leg,pitch]*blend
  w.step(ctrl)
  if step%neural_every==0:
   contact_sum[:]=0;forces[:]=0
   for (pitch,leg),force in w.contacts().items():contact_sum[pitch-21]+=force;forces[leg]+=force
   feedback=np.clip(forces/.05,0,1)
   for idx,force in enumerate(contact_sum):
    pitch=idx+21
    if pitch not in open_notes:
     if force>=.003:
      if np.isnan(on_since[idx]):on_since[idx]=now
      if now-on_since[idx]>=.016 and now-last_off[idx]>=.04:
       event=dict(id=len(actual),pitch=pitch,start=round(float(on_since[idx]),6),end=None,peak_force_uN=float(force));actual.append(event);open_notes[pitch]=event;off_since[idx]=np.nan
     else:on_since[idx]=np.nan
    else:
     event=open_notes[pitch];event['peak_force_uN']=max(event['peak_force_uN'],float(force))
     if force<.0015:
      if np.isnan(off_since[idx]):off_since[idx]=now
      if now-off_since[idx]>=.024:
       event['end']=round(float(off_since[idx]),6);del open_notes[pitch];last_off[idx]=now;on_since[idx]=np.nan
     else:off_since[idx]=np.nan
  if now+dt/2>=next_frame:
   if save:
    frame=np.concatenate([w.pose().ravel(),w.data.qpos[w.key_qids],net.r[net.dn],net.r[net.cpg],amp,forces,gate]).astype('<f4');frames.append(frame)
   next_frame+=1/fps
  if step and step%round(30/dt)==0:print(f'{key}/{variant}: {now:.0f}/{total:.0f}s; elapsed {time.perf_counter()-started:.1f}s',flush=True)
 for event in open_notes.values():event['end']=total
 target=[e for e in notes if e['start']<total and e['end']>e['start']]
 metrics=[match_events(target,actual,tol) for tol in [.025,.05,.1,.15,.25]]
 metadata=dict(piece=key,score_sha256=hashlib.sha256((ROOT/f'data/{key}_score.json').read_bytes()).hexdigest(),variant=variant,seed=seed,duration=total,fps=fps,frame_count=len(frames),geom_count=geom_count,stride=geom_count*12+88+2+18+6+6+6,layout={'pose':[0,geom_count*12],'key_displacement':[geom_count*12,88],'DN':[geom_count*12+88,2],'CPG':[geom_count*12+90,18],'MN':[geom_count*12+108,6],'contact_force':[geom_count*12+114,6],'gate':[geom_count*12+120,6]},dt=dt,neural_dt=neural_dt,notes=notes,actual=actual,metrics=metrics,mujoCo_warnings=int(np.sum(w.data.warning.number)),max_ik_error_mm=float(errors.max()),wall_seconds=time.perf_counter()-started,contact_thresholds_uN=[.003,.0015],retrigger_refractory_s=.04,debounce_on_s=.016,debounce_off_s=.024,controller=('Same score-informed IK scheduler; unity press gate, neural state is an unused observer.' if variant=='constant' else 'Same score-informed IK scheduler; graph modulates press amplitude. Not a learned policy.'),force_units='µN = g·mm/s²',dtype='little-endian float32')
 if save:
  tag=f'{key}_{variant}';array=np.stack(frames);out=ROOT/f'data/{tag}.bin';array.tofile(out);metadata['replay_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(ROOT/f'data/{tag}.json').write_text(json.dumps(metadata,ensure_ascii=False),encoding='utf8')
 print(key,variant,{k:v for k,v in metrics[2].items() if k!='matches'},'wall',metadata['wall_seconds'],flush=True)
 return metadata

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('piece',choices=['merry','pool']);p.add_argument('--variant',default='full');p.add_argument('--duration',type=float);p.add_argument('--dt',type=float,default=.0002);p.add_argument('--seed',type=int,default=0);a=p.parse_args();run(a.piece,a.variant,a.duration,a.dt,a.seed)
