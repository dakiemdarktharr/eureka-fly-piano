"""One shared wall budget; CEM effective-synapse learning; held-out tests.

The one-hour pilot is descriptive, not a powered connectome superiority test.
"""
import argparse,hashlib,os,time,multiprocessing,concurrent.futures
from datetime import datetime,timezone
import numpy as np
from engine import Engine,INITIAL,LOW,HIGH,NAMES,brief,neural
from v4_paths import ROOT,PROJECT,V2,STATE,atomic_json,read_json
E=None;NETS={}
def init():
    global E
    E=Engine()
def job(args):
    seed,variant,theta,task_seed,level,count,deadline=args
    if time.monotonic()>=deadline:return {'cancelled':True,'physics_steps':0}
    key=(seed,variant)
    if key not in NETS:NETS[key]=neural.MotorNetwork(seed=seed,variant='randomized' if variant=='rewired' else 'full',dt=.002)
    E.template=NETS[key];E.variant=variant;E.seed=seed
    notes,d=E.synthetic(task_seed,level,count)
    try:r=E.rollout(theta,notes,d,cancel=lambda:time.monotonic()>=deadline)
    except InterruptedError:return {'cancelled':True,'physics_steps':E.last_steps}
    return {k:v for k,v in r.items() if k not in ['final_qpos','actual','notes']}
def skill_pass(m):return not m.get('solver_warnings',0) and m['precision']>=.95 and m['recall']>=.95
def sequence_pass(m):return not m.get('solver_warnings',0) and m['precision']>.85 and m['recall']>=.85 and m['f1']>=.85
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def aggregate(results):
    ms=[r['metrics'][2] for r in results];nt=sum(m['target_notes'] for m in ms);na=sum(m['actual_notes'] for m in ms);tp=sum(m['matched'] for m in ms)
    p=tp/na if na else 0;r=tp/nt if nt else 0
    return dict(precision=p,recall=r,f1=2*p*r/(p+r) if p+r else 0,matched=tp,target_notes=nt,actual_notes=na,solver_warnings=sum(r['solver_warnings'] for r in results))

def run(minutes=60,workers=3,run_id=None):
    if not 0<minutes<=60:raise ValueError('Global budget must be >0 and <=60 minutes')
    if workers not in range(1,7):raise ValueError('workers must be 1..6')
    run_id=run_id or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    folder=STATE/'runs'/run_id
    if folder.exists():raise ValueError('Existing campaign cannot overwrite or retrain on test')
    folder.mkdir(parents=True)
    start=time.monotonic();deadline=start+minutes*60;train_deadline=start+minutes*60*.88
    config=dict(version=4,run_id=run_id,budget_s=minutes*60,workers=workers,dt=.0002,control_dt=.002,lookahead_s=.15,optimizer='CEM',population=10,elite=3,train_fraction=.88,seeds=[0,1,2],variants=['adaptive','frozen','rewired'],parameter_names=NAMES,train_task_seeds='10000 + generation; never songs',validation_seeds=[71001,71002],test_seeds=[91001,91002,91003,91004],success={'single_precision':.95,'single_recall':.95,'sequence_precision_strict':.85,'sequence_recall':.85,'sequence_f1':.85},hashes={str(p.relative_to(PROJECT)):sha(p) for p in [ROOT/'engine.py',ROOT/'train.py',V2/'world.py',PROJECT/'simulation/model.py',PROJECT/'connectome/weights.npy',PROJECT/'connectome/neurons.csv',V2/'data/ik_cache.npz',V2/'assets/fly_model/piano_fly.xml']},mujoco=__import__('mujoco').__version__,numpy=np.__version__)
    atomic_json(folder/'config.json',config)
    cells=[]
    for seed in config['seeds']:
        for variant in config['variants']:
            cells.append(dict(seed=seed,variant=variant,mean=INITIAL.copy(),sigma=(HIGH-LOW)*.2,best=INITIAL.copy(),best_validation=-1e9,generation=0,level=0,training_steps=0,evaluation_steps=0,history=[],rng=np.random.default_rng(seed+1200),optimization_wall_s=0.,solver_warnings=0,validation=None,skill_pass=False,sequence_pass=False))
    total_steps=0;status={}
    def save(state,message=''):
        elapsed=time.monotonic()-start;view=[]
        for c in cells:
            row={k:v for k,v in c.items() if k not in ['rng','mean','sigma','best']};row['parameters']=c['best'].tolist();view.append(row)
        status.update(state=state,message=message,run_id=run_id,pid=os.getpid(),elapsed_s=elapsed,budget_s=minutes*60,physics_steps=total_steps,aggregate_simulated_s=total_steps*.0002,aggregate_rtf=total_steps*.0002/max(.001,elapsed),cells=view)
        atomic_json(folder/'status.json',status);atomic_json(STATE/'latest.json',{'run_id':run_id})
    def evaluate(pool,c,theta,task_seeds,cutoff,level=0,count=6):
        nonlocal total_steps
        rr=list(pool.map(job,[(c['seed'],c['variant'],theta,s,level,count,cutoff) for s in task_seeds]))
        steps=sum(r['physics_steps'] for r in rr);total_steps+=steps;c['evaluation_steps']+=steps;c['solver_warnings']+=sum(r.get('solver_warnings',0) for r in rr)
        return None if any(r.get('cancelled') for r in rr) else rr
    save('training','Initializing persistent CPU workers')
    try:
        with concurrent.futures.ProcessPoolExecutor(workers,mp_context=multiprocessing.get_context('spawn'),initializer=init) as pool:
            for c in cells:
                rr=evaluate(pool,c,INITIAL,config['validation_seeds'],train_deadline)
                if rr:
                    c['initial_validation']=aggregate(rr);c['best_validation']=c['initial_validation']['f1']+1e-6*np.mean([r['reward'] for r in rr])
                    c['history'].append(dict(wall_s=time.monotonic()-start,cell_optimization_wall_s=0.,generation=0,physics_steps=0,metric=c['initial_validation']))
            while time.monotonic()<train_deadline and not (folder/'stop.request').exists():
                for c in cells:
                    if time.monotonic()>=train_deadline or (folder/'stop.request').exists():break
                    tick=time.monotonic();rng=c['rng'];pop=np.clip(rng.normal(c['mean'],c['sigma'],(10,len(INITIAL))),LOW,HIGH);pop[0]=c['mean'];pop[1]=c['best']
                    if c['variant']=='frozen':pop[:,:24]=0
                    task_seed=10000+c['generation']
                    rr=list(pool.map(job,[(c['seed'],c['variant'],t,task_seed,c['level'],6,train_deadline) for t in pop]))
                    steps=sum(r['physics_steps'] for r in rr);total_steps+=steps;c['training_steps']+=steps;c['solver_warnings']+=sum(r.get('solver_warnings',0) for r in rr);c['optimization_wall_s']+=time.monotonic()-tick
                    good=[i for i,r in enumerate(rr) if not r.get('cancelled')]
                    if len(good)<3:save('training');break
                    elite=sorted(good,key=lambda i:rr[i]['reward'],reverse=True)[:3]
                    c['mean']=.4*c['mean']+.6*pop[elite].mean(0);c['sigma']=np.maximum((HIGH-LOW)*.03,.4*c['sigma']+.6*pop[elite].std(0));c['generation']+=1
                    vr=evaluate(pool,c,c['mean'],config['validation_seeds'],train_deadline)
                    if vr:
                        vm=aggregate(vr);value=vm['f1']+1e-6*np.mean([r['reward'] for r in vr]);c['validation']=vm
                        if value>c['best_validation']:c['best_validation']=value;c['best']=c['mean'].copy()
                        c['skill_pass']=skill_pass(vm)
                        if c['skill_pass']:c['level']=max(1,c['level'])
                        c['history'].append(dict(wall_s=time.monotonic()-start,cell_optimization_wall_s=c['optimization_wall_s'],generation=c['generation'],physics_steps=c['training_steps'],metric=vm,reward=float(np.mean([r['reward'] for r in vr]))))
                    save('training',f"{c['variant']} seed {c['seed']}: generation {c['generation']}")
            save('testing','Frozen selected checkpoints; synthetic tests were not used for selection')
            for c in cells:
                rr=evaluate(pool,c,c['best'],config['test_seeds'],deadline-5)
                if rr is None:c['test']=None;c['test_incomplete']=True
                else:
                    c['test']=aggregate(rr);c['skill_pass']=skill_pass(c['test'])
                    if c['skill_pass']:
                        seq=evaluate(pool,c,c['best'],config['test_seeds'],deadline-5,2,12)
                        if seq:c['sequence_test']=aggregate(seq);c['sequence_pass']=sequence_pass(c['sequence_test'])
                save('testing')
        save('completed','Fixed compute budget ended. Unmet skill gates are not bypassed.')
        atomic_json(ROOT/'results'/f'{run_id}.json',{'config':config,'status':status});return folder
    except BaseException as ex:
        save('failed',repr(ex));raise

def export(run_id):
    folder=STATE/'runs'/run_id;status=read_json(folder/'status.json');out=folder/'replays';out.mkdir(exist_ok=True)
    c=next(c for c in status['cells'] if c['seed']==0 and c['variant']=='adaptive')
    e=Engine(0,'adaptive');notes,d=e.synthetic(91001,count=6);todo=[('skill',notes,d)]
    if c.get('skill_pass') and c.get('sequence_pass'):todo += [(k,*e.song(k)) for k in ['merry','pool']]
    manifest={'run_id':run_id,'qualified_song_demonstration':len(todo)>1,'items':[],'explanation':'Songs unlock only after skill and sequence held-out gates. Skill replay is a diagnostic.'}
    for key,notes,d in todo:
        r,frames=e.rollout(c['parameters'],notes,d,record=True);r['piece']=key;r['diagnostic']=key=='skill'
        frames.tofile(out/f'{key}.bin');r['replay_sha256']=sha(out/f'{key}.bin');atomic_json(out/f'{key}.json',r)
        manifest['items'].append({'piece':key,'physics_steps':r['physics_steps'],'metric':brief(r['metrics'][2])})
    manifest['export_physics_steps']=sum(x['physics_steps'] for x in manifest['items']);manifest['counted_as_training']=False
    atomic_json(folder/'replay_manifest.json',manifest);return manifest

if __name__=='__main__':
    multiprocessing.freeze_support();p=argparse.ArgumentParser();p.add_argument('--minutes',type=float,default=60);p.add_argument('--workers',type=int,default=3);p.add_argument('--export');a=p.parse_args()
    print(export(a.export) if a.export else run(a.minutes,a.workers),flush=True)
