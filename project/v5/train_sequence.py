"""Bounded skill -> two song specialists, with validation-driven plateau recovery.

Engineering parameter search, not a dopamine plasticity model. All optimization
episodes have 100 targets. Test seeds never select or restart the optimizer.
"""
import concurrent.futures as cf
import multiprocessing, os, shutil, time
from datetime import datetime, timezone
import numpy as np
from engine import Engine, LOW, HIGH, NAMES, brief
from train_hundred import clip
from train import sha
from v4_paths import ROOT, PROJECT, V2, STATE, read_json, atomic_json

E = None
SONGS = {}
VALIDATION_SEEDS = (83001, 83002)
TEST_SEEDS = (94001, 94002, 94003)
PROTOCOL = 'v5-precision-curriculum-1'

def init():
    global E, SONGS
    E = Engine()
    SONGS = {k:E.song(k) for k in ('merry','pool')}

def objective(m):
    """Coverage guard prevents a few correct presses from winning by precision."""
    if m.get('solver_warnings',0): return -1e9
    p,r,f = m['precision'],m['recall'],m['f1']
    return p + .5*f - 2*max(0.,.6-r)

def qualify(m):
    return bool(m['precision']>=.8 and m['recall']>=.6 and not m.get('solver_warnings',0))

def combine(rows):
    n=sum(r['metric']['target_notes'] for r in rows)
    a=sum(r['metric']['actual_notes'] for r in rows)
    t=sum(r['metric']['matched'] for r in rows)
    p=t/a if a else 0.;r=t/n if n else 0.
    return dict(target_notes=n,actual_notes=a,matched=t,precision=p,recall=r,
                f1=2*p*r/(p+r) if p+r else 0.,solver_warnings=sum(x['warnings'] for x in rows))

def wilson(t,n):
    if not n:return [0.,1.]
    p=t/n;z=1.96;den=1+z*z/n
    mid=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [float(mid-half),float(mid+half)]

def task(args):
    key,theta,seed_or_offset,level,deadline,stop = args
    notes,duration = E.synthetic(seed_or_offset,level,count=100) if key=='skill' else clip(SONGS[key][0],seed_or_offset)
    def cancelled():return time.monotonic()>=deadline or (stop and __import__('pathlib').Path(stop).exists())
    try:
        result=E.rollout(theta,notes,duration,cancel=cancelled)
        m=brief(result['metrics'][2]);m['solver_warnings']=result['solver_warnings']
        # The physical score dominates. Small bounded shaping breaks ties only approximately.
        value=objective(m)+.01*np.tanh(result['reward'])
        return dict(metric=m,value=float(value),steps=result['physics_steps'],warnings=result['solver_warnings'])
    except InterruptedError:return dict(cancelled=True,steps=E.last_steps,warnings=0)

def population(opt):
    rng=np.random.default_rng();rng.bit_generator.state=opt['rng']
    mean=np.asarray(opt['mean']);best=np.asarray(opt['best']);sigma=np.asarray(opt['sigma'])
    if opt['mode']=='local':
        pop=np.tile(best,(8,1))
        # Pairwise coordinate probes: lateral alignment, press, gate, excitability, cue.
        axes=rng.choice(np.arange(24,55),3,replace=False)
        for j,k in enumerate(axes):
            step=(HIGH[k]-LOW[k])*opt['local_step']
            pop[2+2*j,k]+=step;pop[3+2*j,k]-=step
    else:
        pop=rng.normal(mean,sigma,(8,len(mean)));pop[0]=mean;pop[1]=best
    opt['rng']=rng.bit_generator.state
    return np.clip(pop,LOW,HIGH)

def plateau(opt, improved):
    opt['stale']=0 if improved else opt['stale']+1
    if opt['stale']<4:return None
    opt['stale']=0
    if opt['mode']=='cem':
        opt['mode']='local';opt['local_step']=.08
        return 'CEM plateau: 4 validations without objective gain > 0.005; local coordinate search'
    opt['mode']='cem';opt['restarts']+=1
    opt['mean']=list(opt['best']);opt['sigma']=((HIGH-LOW)*.22).tolist()
    return 'Local plateau: broad CEM restart around retained best checkpoint'

def new_optimizer(theta,seed):
    return dict(mean=list(theta),best=list(theta),sigma=((HIGH-LOW)*.15).tolist(),
                rng=np.random.default_rng(seed).bit_generator.state,mode='cem',stale=0,
                local_step=.08,restarts=0,best_value=-1e9,best_metric=None)

def run(minutes=120,workers=4,skill_minutes=60,resume=True):
    if not 0<minutes<=120 or not 0<skill_minutes<=60 or workers not in range(1,7):raise ValueError('Invalid bounded budget')
    init();previous=read_json(STATE/'latest.json') if (STATE/'latest.json').exists() else {}
    prior_folder=STATE/'runs'/previous.get('run_id','missing')
    checkpoint=prior_folder/'sequence_checkpoint.json'
    continuing=resume and checkpoint.exists() and read_json(checkpoint)['state'] in ['stopped','interrupted','training','exporting','failed']
    if continuing:
        status=read_json(checkpoint);folder=prior_folder;config=read_json(folder/'config.json')
        if config['protocol']!=PROTOCOL:raise ValueError('Incompatible checkpoint protocol')
        workers=config['workers'];status['resumes']=status.get('resumes',0)+1
        (folder/'stop.request').unlink(missing_ok=True)
    else:
        rid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');folder=STATE/'runs'/rid;folder.mkdir(parents=True,exist_ok=False)
        theta=read_json(ROOT/'checkpoints/v4b_primary.json')['parameters']+[0.]*6
        cells=[dict(song=k,variant=k,seed=0,state='queued',budget_s=b*60,elapsed_s=0.,generation=0,
                    training_steps=0,evaluation_steps=0,solver_warnings=0,history=[],switches=[],parameters=theta,
                    optimizer=new_optimizer(theta,5500+i)) for i,(k,b) in enumerate([('skill',skill_minutes),('merry',minutes),('pool',minutes)])]
        status=dict(run_id=rid,kind='skill_then_songs',protocol=PROTOCOL,cells=cells,budget_s=sum(c['budget_s'] for c in cells),state='training')
        config=dict(protocol=PROTOCOL,run_id=rid,workers=workers,skill_minutes=skill_minutes,minutes_per_song=minutes,
                    precision_target=.8,recall_floor=.6,targets_per_episode=100,parameter_names=NAMES,
                    validation_seeds=VALIDATION_SEEDS,test_seeds=TEST_SEEDS,validation_level=1,
                    training_fraction=.85,monitor_every_generations=5,plateau_validations=4,minimum_gain=.005,
                    curriculum='first 25% optimization time level0; rest level1; validation/test always level1',
                    resume='Last atomic generation checkpoint; interrupted work may repeat; stopped time excluded. Uncheckpointed crash time is not reconstructable.',
                    objective='P + 0.5 F1 - 2 max(0,0.6-R); candidate ranking adds 0.01 tanh(legacy reward); no shaping for validation',
                    scope='One exploratory seed; song validation is in-distribution and is not a generalization test.',
                    hashes={str(p.relative_to(PROJECT)):sha(p) for p in [ROOT/'engine.py',ROOT/'train_sequence.py',ROOT/'neural_model.py',V2/'world.py',V2/'data/ik_cache.npz',PROJECT/'connectome/weights.npy',PROJECT/'connectome/neurons.csv',V2/'data/merry_score.json',V2/'data/pool_score.json']})
        atomic_json(folder/'config.json',config)
    status['pid']=os.getpid();out=folder/'replays';out.mkdir(exist_ok=True)
    manifest_path=folder/'replay_manifest.json'
    manifest=read_json(manifest_path) if manifest_path.exists() else dict(run_id=status['run_id'],kind='skill_then_songs',qualified_song_demonstration=False,items=[])
    if not manifest['items']:
        source=prior_folder/'replays'
        if not (source/'skill.bin').exists():source=STATE/'preview'
        for ext in ['json','bin']:
            if (source/f'skill.{ext}').exists():shutil.copy2(source/f'skill.{ext}',out/f'skill.{ext}')
        if (out/'skill.bin').exists():manifest['items']=[dict(piece='skill',prior_diagnostic=True)]
        atomic_json(manifest_path,manifest)
    active=None;clock=0.;base=0.
    def stopped():return (folder/'stop.request').exists()
    def save(state,message):
        if active is not None:active['elapsed_s']=base+time.monotonic()-clock
        status.update(state=state,message=message,elapsed_s=sum(c['elapsed_s'] for c in status['cells']))
        steps=sum(c['training_steps']+c['evaluation_steps'] for c in status['cells'])
        status.update(physics_steps=steps,aggregate_simulated_s=steps*.0002,aggregate_rtf=steps*.0002/max(.001,status['elapsed_s']))
        atomic_json(folder/'sequence_checkpoint.json',status)
        public={**status,'cells':[{k:v for k,v in c.items() if k!='optimizer'} for c in status['cells']]}
        atomic_json(folder/'status.json',public);atomic_json(STATE/'latest.json',dict(run_id=status['run_id']))
    save('training','Học kỹ năng 100 nốt → Merry → Pool. Mục tiêu P ≥80%, R ≥60%; chưa phải kết quả.')
    try:
        with cf.ProcessPoolExecutor(workers,mp_context=multiprocessing.get_context('spawn'),initializer=init) as pool:
            for c in status['cells']:
                if c['state']=='completed':continue
                if stopped():break
                key=c['song'];active=c;base=c['elapsed_s'];clock=time.monotonic()
                deadline=clock+max(0,c['budget_s']-base);train_end=clock+max(0,c['budget_s']*.85-base)
                if c['state']=='queued' and key!='skill':
                    skill=status['cells'][0]['parameters'];c['parameters']=skill.copy();c['optimizer']=new_optimizer(skill,5500+status['cells'].index(c))
                opt=c['optimizer'];c['state']='training'
                bins=None if key=='skill' else sorted(set(list(range(0,len(SONGS[key][0])-99,100))+[len(SONGS[key][0])-100]))
                monitors=list(VALIDATION_SEEDS) if key=='skill' else [bins[len(bins)//3],bins[2*len(bins)//3]]
                def measure(theta,indices,limit):
                    rows=list(pool.map(task,[(key,theta,x,1,limit,str(folder/'stop.request')) for x in indices]))
                    c['evaluation_steps']+=sum(r['steps'] for r in rows);c['solver_warnings']+=sum(r['warnings'] for r in rows)
                    return None if any(r.get('cancelled') for r in rows) else combine(rows)
                if opt['best_metric'] is None and time.monotonic()<train_end:
                    vm=measure(opt['best'],monitors,train_end)
                    if vm:
                        opt['best_metric']=vm;opt['best_value']=objective(vm);c['initial_validation']=vm;c['validation']=vm
                        c['history'].append(dict(wall_s=sum(x['elapsed_s'] for x in status['cells'])+time.monotonic()-clock,generation=0,metric=vm))
                while time.monotonic()<train_end and not stopped():
                    elapsed=base+time.monotonic()-clock;level=0 if key=='skill' and elapsed<c['budget_s']*.85*.25 else 1
                    pop=population(opt);gen=c['generation'];index=100000+gen if key=='skill' else bins[gen%len(bins)]
                    rows=list(pool.map(task,[(key,t,index,level,train_end,str(folder/'stop.request')) for t in pop]))
                    c['training_steps']+=sum(r['steps'] for r in rows);c['solver_warnings']+=sum(r['warnings'] for r in rows)
                    good=[i for i,r in enumerate(rows) if not r.get('cancelled') and not r['warnings']]
                    if len(good)<3:break
                    elite=sorted(good,key=lambda i:rows[i]['value'],reverse=True)[:3];candidate=pop[elite[0]]
                    if opt['mode']=='cem':
                        mean=np.asarray(opt['mean']);sigma=np.asarray(opt['sigma'])
                        opt['mean']=(.4*mean+.6*pop[elite].mean(0)).tolist()
                        opt['sigma']=np.maximum((HIGH-LOW)*.03,.4*sigma+.6*pop[elite].std(0)).tolist()
                    else:opt['mean']=candidate.tolist()
                    c['generation']+=1;c['last_episode_targets']=100;c['curriculum_level']=level
                    # Local search validates each probe batch; global CEM every five generations.
                    if c['generation']%5==0 or opt['mode']=='local':
                        vm=measure(candidate.tolist(),monitors,train_end)
                        if vm:
                            improved=objective(vm)>opt['best_value']+.005
                            if objective(vm)>opt['best_value']:
                                opt['best_value']=objective(vm);opt['best']=candidate.tolist();opt['best_metric']=vm;c['parameters']=candidate.tolist()
                            c['validation']=opt['best_metric']
                            c['history'].append(dict(wall_s=sum(x['elapsed_s'] for x in status['cells'])+(base+time.monotonic()-clock-c['elapsed_s']),generation=c['generation'],metric=vm,mode=opt['mode'],level=level))
                            switch=plateau(opt,improved)
                            if switch:c['switches'].append(dict(generation=c['generation'],reason=switch))
                    c['optimizer_mode']=opt['mode'];c['validation_target_met']=qualify(opt['best_metric']) if opt['best_metric'] else False
                    save('training',f"{key}: thế hệ {c['generation']} · {opt['mode']} · 100 nốt/lượt · mục tiêu P80/R60.")
                if stopped():c['state']='stopped';save('stopped','Đã lưu checkpoint; bấm Học tiếp để tiếp tục ngân sách còn lại.');active=None;break
                c['state']='exporting';save('exporting',f'{key}: đánh giá checkpoint cố định và ghi hoạt động 412 neuron.')
                if key=='skill' and 'test' not in c:
                    test=measure(c['parameters'],list(TEST_SEEDS),deadline)
                    if test:
                        c['test']=test;c['target_met']=qualify(test)
                        c['precision_wilson95']=wilson(test['matched'],test['actual_notes'])
                        c['recall_wilson95']=wilson(test['matched'],test['target_notes'])
                    else:c['test_incomplete']=True
                if time.monotonic()<deadline and not stopped():
                    notes,duration=E.synthetic(TEST_SEEDS[0],1,count=100) if key=='skill' else SONGS[key]
                    try:
                        result,trace=E.rollout(c['parameters'],notes,duration,record=True,cancel=lambda:time.monotonic()>=deadline or stopped())
                        c['evaluation_steps']+=result['physics_steps'];c['solver_warnings']+=result['solver_warnings']
                        m=brief(result['metrics'][2]);m['solver_warnings']=result['solver_warnings']
                        if key!='skill':c['test']=m;c['target_met']=qualify(m)
                        result.update(piece=key,checkpoint_label=f"{key} / {status['run_id']}",diagnostic=True,protocol=PROTOCOL,
                                      evaluation_scope='Held-out synthetic sequence' if key=='skill' else 'Practiced full song, in-distribution')
                        trace.tofile(out/f'{key}.bin');result['replay_sha256']=sha(out/f'{key}.bin');atomic_json(out/f'{key}.json',result)
                        manifest['items']=[x for x in manifest['items'] if x['piece']!=key]+[dict(piece=key,metric=m)]
                        manifest['qualified_song_demonstration']=bool(status['cells'][0].get('target_met',False))
                        atomic_json(manifest_path,manifest);c['replay_written']=True
                    except InterruptedError:c['evaluation_steps']+=E.last_steps;c['replay_incomplete']=True
                if stopped():c['state']='stopped';save('stopped','Checkpoint đã lưu; có thể tiếp tục phần đánh giá còn lại.');active=None;break
                c['state']='completed';save('training',f'{key}: kết thúc ngân sách; chuyển giai đoạn tiếp theo.');active=None
        final='stopped' if stopped() else ('completed' if all(c.get('replay_written') and c.get('test') for c in status['cells']) else 'incomplete')
        save(final,'Đã kết thúc ba giai đoạn. Đọc cột P/R/F1 và trạng thái đạt mục tiêu; hoàn tất ngân sách không đồng nghĩa đạt 80%.')
        return folder
    except BaseException as ex:
        save('failed',repr(ex));raise

if __name__=='__main__':
    multiprocessing.freeze_support()
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--minutes',type=float,default=120);p.add_argument('--skill-minutes',type=float,default=60);p.add_argument('--workers',type=int,default=4);p.add_argument('--fresh',action='store_true');a=p.parse_args()
    print(run(a.minutes,a.workers,a.skill_minutes,not a.fresh),flush=True)
