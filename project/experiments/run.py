from pathlib import Path
import sys,json,hashlib,subprocess,time
import numpy as np
from scipy.signal import periodogram,hilbert
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulation.model import MotorNetwork,ROOT
from body.dynamics import Body
from connectome.prepare import dump,sha
from experiments.registry import registry

def events_for(cfg):
    if cfg.get('event_file'):
        payload=json.loads(Path(cfg['event_file']).read_text(encoding='utf-8-sig'))
        events=payload['events'] if isinstance(payload,dict) else payload
        previous=-1.
        for i,event in enumerate(events):
            if not 0<=event['key']<cfg['nkeys'] or int(event['key'])!=event['key']:raise ValueError('Key out of range')
            if not np.isfinite(event['time']) or event['time']<0 or not previous<event['time']<cfg['duration']:raise ValueError('Events must have strictly increasing finite times inside the trial')
            previous=event['time'];event['event_id']=i;event.setdefault('hold',.13)
            if not 0<event['hold']<=1:raise ValueError('Hold must be within (0,1] seconds')
        return events
    if cfg['experiment_id']=='A1':return []
    rng=np.random.default_rng(9100+cfg['seed']%3)
    cond=cfg['condition'];duration=cfg['duration']
    times=np.arange(1,duration-.4,.55)
    if cond=='long':times=np.arange(.5,duration-.3,.32)
    if cond=='syncopated':times=np.cumsum(np.resize([.35,.7,.35,.5],12))+.5;times=times[times<duration-.4]
    keys=rng.integers(0,cfg['nkeys'],len(times))
    if cond in ['repeated','alternating']:keys=np.resize([0,2,1,3] if cond=='repeated' else [0,7],len(times))
    return [{'event_id':i,'time':float(t),'key':int(k),'hold':.13} for i,(t,k) in enumerate(zip(times,keys))]

def score_contacts(events,contacts,tolerance=.25):
    # One-to-one nearest-time same-key matches. Unmatched extra contacts are retained.
    unused=set(range(len(contacts)));matches=[]
    for e in events:
        candidates=[i for i in unused if contacts[i]['key']==e['key'] and abs(contacts[i]['time']-e['time'])<=tolerance]
        if candidates:
            i=min(candidates,key=lambda i:abs(contacts[i]['time']-e['time']));unused.remove(i)
            matches.append(dict(event_id=e['event_id'],contact_index=i,error_s=contacts[i]['time']-e['time']))
    err=np.array([m['error_s'] for m in matches])
    return dict(key_accuracy=len(matches)/len(events) if events else None,
      timing_mae_s=float(abs(err).mean()) if len(err) else None,
      timing_jitter_s=float(err.std(ddof=1)) if len(err)>1 else None,
      misses=len(events)-len(matches),extra_contacts=len(unused),matches=matches,
      precision=len(matches)/len(contacts) if contacts else 0.,sequence_completion=int(len(matches)==len(events)) if events else None)

def neural_metrics(rates,dt,mn_indices):
    x=rates[len(rates)//2:,mn_indices]
    f,p=periodogram(x,fs=1/dt,axis=0)
    mask=(f>=1)&(f<=40)
    powers=p[mask];peak=powers.max(0) if powers.size else np.zeros(x.shape[1])
    var=x.var(0);active=(var>.1)&(x.max(0)>1)
    concentration=peak/(p.sum(0)+1e-12)
    dominant=f[mask][powers.argmax(0)]
    return {'motor_rhythm_power':float(concentration[active].mean()) if active.any() else 0.,
      'oscillating_mn_fraction':float(active.mean()),'motor_frequency_hz':float(dominant[active].mean()) if active.any() else None,
      'rate_mean_hz':float(rates.mean()),'rate_max_hz':float(rates.max()),
      'population_variance':float(var.mean())}

def run(cfg,output_root=None):
    tic=time.perf_counter();dt=cfg['dt'];variant=cfg['variant'];cond=cfg['condition'];exp=cfg['experiment_id']
    net=MotorNetwork(cfg['seed'],variant,dt)
    disabled=0 if cond=='disable_LF' else 2 if cond=='disable_LM' else -1
    layout=cond if cond in ['mirrored','shifted','spacing','height'] else 'standard'
    body=Body(cfg['nkeys'],layout,disabled);standard=Body(cfg['nkeys'])
    events=events_for(cfg);n=int(round(cfg['duration']/dt));t=np.arange(n)*dt
    # Full-resolution rates/body are the sole analysis and presentation source.
    rates=np.zeros((n,len(net.r)),np.float32);task=np.zeros((n,8),np.float32)
    q=np.zeros((n,6,2),np.float32);dq=q.copy();torque=q.copy();force=np.zeros((n,6),np.float32)
    targets=np.full(n,-1,int);actual=np.full((n,6),-1,int);allocation=np.full(n,-1,int)
    contacts=[];event_i=-1;limb=0;key=-1;cue=True;fb=np.zeros(6);fb_history=[];previous_amp=np.zeros(6)
    rng=np.random.default_rng(cfg['seed']+5000)
    for k,now in enumerate(t):
        while event_i+1<len(events) and now>=events[event_i+1]['time']-.2:
            event_i+=1;key=events[event_i]['key']
        cue=not (exp=='A3' and 3<now<5)
        drive=np.full(2,cfg.get('drive',500.))
        if exp=='A2' and now>=4:
            drive*=dict(up_small=1.2,up_large=1.5,down_small=.8,down_large=.5)[cond]
        if exp=='A5':
            if cond=='weak':drive*=.5
            if cond=='strong':drive*=1.5
            if cond=='late' and now<2:drive*=0
            if cond=='left_bias':drive[1]=0
        if now<.25:drive*=0
        fb_history.append(fb.copy());feedback=fb
        if cond=='delayed':feedback=fb_history[max(0,k-round(.08/dt))]
        if cond=='noisy':feedback=fb+rng.normal(0,.25,6)
        amp=net.step(drive,key,feedback,cue)
        if variant=='hand_cpg':amp=.55+.5*np.sin(2*np.pi*8*now+np.array([0,np.pi,np.pi,0,0,np.pi]))
        if variant in ['direct','sequence_specific']:amp=np.ones(6)
        decoded=int(np.argmax(net.task)) if net.task.max()>.2 else -1
        if decoded>=0:
            if variant in ['direct','sequence_specific']:limb=decoded%6
            else:
                available=[i for i in range(6) if i!=disabled]
                # Cost depends on actual joint posture; key identity is never a fixed limb ID.
                limb=min(available,key=lambda i:np.linalg.norm(body.ik(i,body.x[decoded],body.height)-body.q[i]))
            if cond=='forced_RF':limb=1
        desired=np.array([body.ik(i,body.hips[i,0],-.62) for i in range(6)])
        if exp=='A1':
            for i in range(6):desired[i]=body.ik(i,body.hips[i,0],-.64-.25*np.clip(amp[i],0,1))
        elif decoded>=0 and event_i>=0:
            event=events[event_i];age=now-event['time'];press=0<=age<event['hold']
            # The body decoder is explicitly timed by the task sequencer. This is
            # an engineered shortcut requiring attribution, not connectomic timing inference.
            if variant=='sequence_specific' and cfg['split']=='test':decoded=event_i%cfg['nkeys']
            mapping=standard if variant in ['no_body_mapping','direct','sequence_specific'] else body
            x=mapping.x[decoded];z=mapping.height+.14
            if cond=='curved_reach' and age<0:x+=.08*np.sin(np.pi*np.clip((age+.2)/.2,0,1))
            if variant=='no_memory' and age<0: x=body.hips[limb,0];z=-.62
            if press and amp[limb]>.005:z=mapping.height-.055*np.clip(amp[limb],.2,1)
            desired[limb]=body.ik(limb,x,z)
            targets[k]=event['key'];allocation[k]=limb
        rising=body.step(desired,dt,kp=22 if cond=='soft_force' else 32)
        fb=np.clip((body.q-desired).mean(1)*2,-1,1)+np.clip(body.force,0,1)*.05
        for i in np.flatnonzero(rising):
            m=net.mn[i];resp=int(m[np.argmax(net.r[m])]) if len(m) else -1
            expected=events[event_i] if event_i>=0 else None
            contacts.append({'time':float(now),'key':int(body.actual[i]),'limb':int(i),
             'force':float(body.force[i]),'responsible_mn_id':str(net.table.iloc[resp].id) if resp>=0 else None,
             'attribution':'highest active member of engineered population readout; not proven sole causal neuron',
             'expected_key':expected['key'] if expected else None,'timing_error_s':float(now-expected['time']) if expected else None})
        rates[k]=net.r;task[k]=net.task;q[k]=body.q;dq[k]=body.dq;torque[k]=body.tau;force[k]=body.force;actual[k]=body.actual
    metrics=neural_metrics(rates,dt,np.concatenate(net.mn));metrics.update(score_contacts(events,contacts))
    metrics.update({'energy_proxy':float(np.sum(abs(torque*dq))*dt),'smoothness_accel_rms':float(np.sqrt(np.mean(np.diff(dq,axis=0)**2))/dt),
      'joint_velocity_rms':float(np.sqrt(np.mean(dq**2))),'torque_rms':float(np.sqrt(np.mean(torque**2))),
      'contact_count':len(contacts),'rewire_swaps':net.swap_count,'wall_seconds':time.perf_counter()-tic,
      'adaptation_trials':None,'training_improvement':None,'spike_metrics':None})
    out=(Path(output_root) if output_root else ROOT/'data/runs')/cfg['run_id'];out.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out/'telemetry.npz',time=t,rates=rates,task=task,q=q,dq=dq,torque=torque,force=force,actual=actual,target=targets,limb=allocation,key_x=body.x,key_height=body.height,hips=body.hips)
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit='uncommitted'
    meta={**cfg,'git_commit':commit,'config_sha256':hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest(),
      'dataset_version':net.manifest['dataset_version'],'graph_sha256':net.manifest['graph_sha256'],
      'telemetry_sha256':sha(out/'telemetry.npz'),'body_version':net.manifest['body_model'],
      'activity_scale_hz':[0,250],'spikes':'not simulated; rate model','events':events,'contacts':contacts}
    dump(out/'metadata.json',meta);dump(out/'metrics.json',metrics)
    return metrics

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--id');p.add_argument('--all',action='store_true');p.add_argument('--seeds',type=int,default=8);p.add_argument('--output');p.add_argument('--events');a=p.parse_args()
    configs=registry(range(a.seeds))
    if a.id:configs=[c for c in configs if c['run_id']==a.id]
    elif not a.all:configs=configs[:1]
    if not configs:raise SystemExit('No matching experiment ID')
    for c in configs:
        if a.events: c=dict(c,event_file=str(Path(a.events).resolve()),run_id=c['run_id']+'_external')
        m=run(c,a.output);print(c['run_id'],json.dumps({k:m[k] for k in ['motor_rhythm_power','motor_frequency_hz','key_accuracy','timing_mae_s','wall_seconds']}),flush=True)


