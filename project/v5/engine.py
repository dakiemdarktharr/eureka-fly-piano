"""V4 hybrid controller. Learned effective synapses; score-to-IK stays engineered.

Physics is unchanged (MuJoCo 3.9, dt=0.2 ms, noslip enabled). Only calls to
identical held-control steps are batched. No visual frames during optimization.
"""
import copy, time
import numpy as np
import mujoco as mj
from v4_paths import PROJECT,V2,read_json
import world,simulate
world.ROOT=V2;simulate.ROOT=V2
from world import PianoWorld
from simulate import schedule,match_events
import neural_model as neural
neural.ROOT=PROJECT

NAMES=([f'log_synapse_CPG_{i}' for i in range(18)]+[f'log_synapse_MN_{i}' for i in range(6)]+
       [f'log_gate_{i}' for i in range(6)]+[f'press_extension_{i}' for i in range(6)]+[f'MN_excitability_{i}' for i in range(6)]+[f'lateral_bias_mm_{i}' for i in range(6)]+['press_advance_s']+[f'goal_cue_E1_{i}' for i in range(6)])
LOW=np.array([-.69]*24+[-1.4]*6+[-.25]*6+[-50.]*6+[-.275]*6+[0.]+[0.]*6)
HIGH=np.array([.69]*24+[1.4]*6+[.5]*6+[50.]*6+[.275]*6+[.08]+[50.]*6)
INITIAL=np.zeros(55);INITIAL[48]=.02

def brief(m):return {k:v for k,v in m.items() if k!='matches'}

class Detector:
    """Fixed physical-contact debounce, global to all 88 keys."""
    def __init__(self):
        self.on=np.full(88,np.nan);self.off=self.on.copy();self.last=np.full(88,-10.)
        self.open={};self.events=[]
    def step(self,force,t):
        for k,f in enumerate(force):
            p=k+21
            if p not in self.open:
                if f>=.003:
                    if np.isnan(self.on[k]):self.on[k]=t
                    if t-self.on[k]>=.016 and t-self.last[k]>=.04:
                        e=dict(id=len(self.events),pitch=p,start=round(float(self.on[k]),6),end=None,peak_force_uN=float(f))
                        self.events.append(e);self.open[p]=e;self.off[k]=np.nan
                else:self.on[k]=np.nan
            else:
                self.open[p]['peak_force_uN']=max(self.open[p]['peak_force_uN'],float(f))
                if f<.0015:
                    if np.isnan(self.off[k]):self.off[k]=t
                    if t-self.off[k]>=.024:
                        self.open[p]['end']=round(float(self.off[k]),6);del self.open[p]
                        self.last[k]=t;self.on[k]=np.nan
                else:self.off[k]=np.nan
    def finish(self,duration):
        for e in self.open.values():e['end']=duration
        return self.events

class Engine:
    def __init__(self,seed=0,variant='adaptive',dt=.0002):
        self.seed=seed;self.variant=variant;self.dt=dt;self.w=PianoWorld(dt)
        c=np.load(V2/'data/ik_cache.npz');self.hover=c['hover'];self.press=c['press'];self.errors=c['error']
        self.template=neural.MotorNetwork(seed=seed,variant='randomized' if variant=='rewired' else ('full' if variant in ['adaptive','frozen'] else variant),dt=.002)
        self.group=np.zeros(len(self.template.r),int)
        for i,k in enumerate(self.template.cpg):self.group[k]=i
        for i,ids in enumerate(self.template.mn):self.group[ids]=18+i
        self.idle=self.w.neutral_ctrl.copy()
        for l in range(6):
            pitch=int(np.clip(round(self.w.neutral_feet[l,1]/.055+64),21,108))
            self.idle[self.w.acts[l]]=self.hover[l,pitch-21]
        self.pitches=[np.argsort(self.errors[l])[:12]+21 for l in range(6)]
        self.geoms=[i for i in range(self.w.model.ngeom) if self.w.model.geom_type[i]==mj.mjtGeom.mjGEOM_MESH]

    def motor_gate(self,net,amp,theta):
        return np.clip(8*amp*np.exp(theta[24:30]),0,1)

    def synthetic(self,seed,level=0,count=100):
        if count<=0:raise ValueError("Positive target count required")
        rng=np.random.default_rng(seed);notes=[]
        for i in range(count):
            leg=i%6;pool=self.pitches[leg][:3 if level==0 else 12]
            pitch=int(rng.choice(pool));start=.4+i*(.55 if level<2 else .3)
            notes.append(dict(id=i,pitch=pitch,start=start,end=start+(.22 if level<2 else .16),leg=leg))
        return notes,notes[-1]['end']+.35

    def song(self,key):
        s=read_json(V2/f'data/{key}_score.json')
        return schedule(s,self.errors),s['duration']+1

    def rollout(self,theta,notes,duration,record=False,batched=True,cancel=None):
        theta=np.asarray(theta,float)
        if theta.shape!=INITIAL.shape or not np.isfinite(theta).all() or np.any(theta<LOW) or np.any(theta>HIGH):raise ValueError('Invalid theta')
        w=self.w;m=w.model;d=w.data;net=copy.deepcopy(self.template)
        if self.variant!='frozen':
            # Row = postsynaptic node. Positive factors preserve graph and signs.
            scales=np.exp(theta[:24][self.group]);scales[net.dn]=1
            net.w.data*=np.repeat(scales,np.diff(net.w.indptr))
        for leg,ids in enumerate(net.mn):net.th[ids]-=theta[36+leg]
        for _ in range(100):amp=net.step(500,-1)
        mj.mj_resetDataKeyframe(m,d,0);mj.mj_forward(m,d)
        seqs=[[e for e in notes if e['leg']==l] for l in range(6)];ptr=np.zeros(6,int)
        goal_drive=np.zeros(6)
        detector=Detector();forces=np.zeros(6);contact=np.zeros(88);feedback=np.zeros(6)
        frames=[];nextframe=0.;energy=0.;dense=0.;warn=0
        n=round(duration/.002);stride=round(.002/self.dt);steps=0;self.last_steps=0
        for j in range(n):
            t=j*.002
            if j%50==0 and cancel and cancel():raise InterruptedError('Cancelled')
            amp=net.step(500,-1,feedback,goal_drive=goal_drive);goal_drive[:]=0;gate=self.motor_gate(net,amp,theta)
            ctrl=self.idle.copy();wanted=[]
            for l,seq in enumerate(seqs):
                while ptr[l]<len(seq) and seq[ptr[l]]['end']+.05<t:ptr[l]+=1
                if ptr[l]>=len(seq):continue
                e=seq[ptr[l]]
                # Scheduler reveals at most 150 ms; no whole-song memory input.
                if t<e['start']-.15:continue
                if t<e['end']:goal_drive[l]=theta[49+l]
                idx=float(np.clip(e['pitch']-21+theta[42+l]/.055,0,87));lo=int(idx);hi=min(87,lo+1);f=idx-lo
                h=(1-f)*self.hover[l,lo]+f*self.hover[l,hi];p=(1-f)*self.press[l,lo]+f*self.press[l,hi]
                blend=gate[l]*(1+theta[30+l]) if e['start']-theta[48]<=t<e['end'] else 0.
                ctrl[w.acts[l]]=h+blend*(p-h)
                if e['start']<=t<e['end']:wanted.append((e['pitch'],l))
            d.ctrl[:]=ctrl
            # Same sample phase as v3: first physical step, sample, then 9 steps.
            mj.mj_step(m,d);steps+=1
            forces[:]=0;contact[:]=0
            for (pitch,l),f in w.contacts().items():contact[pitch-21]+=f;forces[l]+=f
            detector.step(contact,t);feedback=np.clip(forces/.05,0,1)
            energy+=float(np.sum(np.abs(d.actuator_force*d.actuator_velocity)))*.002
            for pitch,l in wanted:
                dense+=float(np.exp(-np.linalg.norm(d.xpos[w.toes[l]]-w.target(l,pitch,-.15))/.08))*.002/max(1,len(wanted))
            if record and t+.001>=nextframe:
                frames.append(np.concatenate([w.pose().ravel(),d.qpos[w.key_qids],net.r[net.dn],net.r[net.cpg],amp,forces,gate,net.r]).astype('<f4'));nextframe+=1/24
            if batched:mj.mj_step(m,d,nstep=stride-1)
            else:
                for _ in range(stride-1):w.step(ctrl)
            steps+=stride-1;self.last_steps=steps
            if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():raise FloatingPointError('Nonfinite physics')
            warn=max(warn,int(np.sum(d.warning.number)))
        duration=n*.002;actual=detector.finish(duration)
        metrics=[match_events(notes,actual,t) for t in [.025,.05,.1,.15,.25]];metric=metrics[2]
        by_t={e['id']:e for e in notes};by_a={e['id']:e for e in actual};ious=[]
        for tid,aid,_ in metric['matches']:
            a=by_t[tid];b=by_a[aid];inter=max(0,min(a['end'],b['end'])-max(a['start'],b['start']))
            ious.append(inter/(max(a['end'],b['end'])-min(a['start'],b['start'])))
        iou=float(np.mean(ious)) if ious else 0.
        nt=max(1,len(notes));timing=metric['conditional_mae_s'] or 0
        # Episode reward; each target can earn once. Dense term <= .1.
        reward=(5*metric['matched']-2*metric['missed']-metric['extra'])/nt+ .5*iou-.5*timing/.1+.1*dense/max(duration,.002)-min(.1,energy*1e-5)
        if warn:reward=-1e6
        result=dict(metrics=metrics,reward=float(reward),matched_duration_iou=iou,notes=notes,actual=actual,duration=duration,physics_steps=steps,physics_seconds=steps*self.dt,solver_warnings=warn,final_qpos=d.qpos.tolist(),actuator_work_uN_mm=energy)
        if record:
            g=len(self.geoms);result.update(piece='skill',variant=self.variant,seed=self.seed,fps=24,frame_count=len(frames),geom_count=g,stride=g*12+126+len(net.r),neuron_ids=net.table.bodyId.astype(str).tolist(),activity_units="model rate units; not spikes or calibrated Hz",activity_threshold=1.,layout={'pose':[0,g*12],'key_displacement':[g*12,88],'DN':[g*12+88,2],'CPG':[g*12+90,18],'MN':[g*12+108,6],'contact_force':[g*12+114,6],'gate':[g*12+120,6],'neuron_rates':[g*12+126,len(net.r)]},dt=self.dt,neural_dt=.002,dtype='little-endian float32',controller='Hybrid: learned effective synaptic gains + motor gate; engineered score-to-IK; 150 ms lookahead',parameters=theta.tolist(),goal_cue_scope='Engineered 150 ms target-to-E1 sensory projection; six learned gains 0..50')
            return result,np.stack(frames)
        return result
