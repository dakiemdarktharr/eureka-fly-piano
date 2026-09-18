"""Two independent song specialists; no precision prerequisite or early success stop.

All score onsets are eligible for practice. Monitoring and full-song replays are
in-distribution diagnostics, not held-out generalization tests. V4 study is preserved.
"""
import argparse, concurrent.futures, multiprocessing, os, shutil, time
from datetime import datetime, timezone
import numpy as np
from engine import Engine, LOW, HIGH, NAMES, brief
from train import aggregate, sha
from v4_paths import ROOT, V2, PROJECT, STATE, atomic_json, read_json

E = None
SONGS = {}

def init():
    global E, SONGS
    E = Engine(0, 'adaptive')
    SONGS = {key: E.song(key) for key in ('merry', 'pool')}

def clip(notes, offset, width=4.):
    # Preserve original event IDs, durations and full-song leg assignments.
    selected = [dict(n, start=n['start']-offset+.4, end=n['end']-offset+.4)
                for n in notes if offset <= n['start'] < offset+width]
    return selected, max([width+.75]+[n['end']+.35 for n in selected])

def job(args):
    key, theta, offsets, deadline = args
    results = []; steps = 0
    for offset in offsets:
        if time.monotonic() >= deadline: return dict(cancelled=True, physics_steps=steps)
        notes, duration = clip(SONGS[key][0], offset)
        try:
            r = E.rollout(theta, notes, duration, cancel=lambda: time.monotonic() >= deadline)
        except InterruptedError:
            return dict(cancelled=True, physics_steps=steps+E.last_steps)
        steps += r['physics_steps']; results.append(r)
    return dict(physics_steps=steps, metric=aggregate(results),
                reward=float(np.mean([r['reward'] for r in results])),
                solver_warnings=sum(r['solver_warnings'] for r in results))

def validate_budget(minutes, workers):
    if not np.isfinite(minutes) or not 0 < minutes <= 120: raise ValueError('0 < minutes per song <= 120')
    if workers not in range(1,7): raise ValueError('1..6 workers')

def run(minutes=120, workers=4):
    validate_budget(minutes, workers)
    source = read_json(ROOT/'checkpoints/v4b_primary.json')
    initial = np.asarray(source['parameters'], float)
    if initial.shape != LOW.shape or not np.isfinite(initial).all() or np.any(initial<LOW) or np.any(initial>HIGH): raise ValueError('Invalid warm start')
    rid = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    folder = STATE/'runs'/rid; folder.mkdir(parents=True, exist_ok=False)
    out = folder/'replays'; out.mkdir()
    init(); start = time.monotonic(); total = minutes*120
    config = dict(version=4, kind='song_practice', run_id=rid, minutes_per_song=minutes,
                  budget_s=total, workers=workers, songs=['merry','pool'], warm_start=source,
                  precision_gate=None, optimizer='CEM', population=8, elite=3,
                  parameter_names=NAMES, seed=0, dt=.0002, clip_onset_width_s=4,
                  training_fraction=.90, monitor_every_generations=5,
                  evaluation_scope='Practiced songs; no held-out generalization claim',
                  score_policy='Original voice events retained, including unisons and unassigned notes; no note filtering',
                  hashes={str(p.relative_to(PROJECT)):sha(p) for p in [ROOT/'engine.py',ROOT/'train_songs.py',V2/'world.py',PROJECT/'simulation/model.py',PROJECT/'connectome/weights.npy',PROJECT/'connectome/neurons.csv',V2/'data/ik_cache.npz',V2/'assets/fly_model/piano_fly.xml',V2/'data/merry_score.json',V2/'data/pool_score.json']},
                  numpy=np.__version__, mujoco=__import__('mujoco').__version__)
    atomic_json(folder/'config.json', config)
    cells = [dict(song=k, variant=k, seed=0, generation=0, training_steps=0, evaluation_steps=0,
                  solver_warnings=0, history=[], parameters=initial.tolist(), state='queued',
                  covered_note_ids=[], total_target_notes=len(SONGS[k][0])) for k in config['songs']]
    status = dict(run_id=rid, kind='song_practice', pid=os.getpid(), budget_s=total, cells=cells)
    manifest = dict(run_id=rid, kind='song_practice', precision_gate=None,
                    qualified_song_demonstration=False, items=[], counted_as_training=False,
                    explanation='Bài đã luyện; xuất replay không phụ thuộc precision. Không phải kiểm tra khái quát hóa.')
    # Keep the old diagnostic available while the first song is being trained.
    previous = read_json(STATE/'latest.json') if (STATE/'latest.json').exists() else {}
    old = STATE/'runs'/previous.get('run_id','missing')/'replays'
    for suffix in ('json','bin'):
        if (old/f'skill.{suffix}').exists(): shutil.copy2(old/f'skill.{suffix}',out/f'skill.{suffix}')
    if (out/'skill.json').exists() and (out/'skill.bin').exists(): manifest['items'].append(dict(piece='skill',prior_diagnostic=True))
    atomic_json(folder/'replay_manifest.json',manifest)
    def save(state, message):
        elapsed = time.monotonic()-start
        steps = sum(c['training_steps']+c['evaluation_steps'] for c in cells)
        status.update(state=state,message=message,elapsed_s=elapsed,physics_steps=steps,
                      aggregate_simulated_s=steps*.0002,aggregate_rtf=steps*.0002/max(.001,elapsed))
        atomic_json(folder/'status.json',status); atomic_json(STATE/'latest.json',dict(run_id=rid))
    def stopped(): return (folder/'stop.request').exists()
    save('training',f'Luyện trực tiếp hai bài; {minutes:g} phút mỗi bài; không có ngưỡng precision.')
    try:
        with concurrent.futures.ProcessPoolExecutor(workers,mp_context=multiprocessing.get_context('spawn'),initializer=init) as pool:
            for index,c in enumerate(cells):
                if stopped(): break
                key=c['song']; song_start=time.monotonic(); deadline=song_start+minutes*60
                train_end=song_start+minutes*60*.90
                notes,duration=SONGS[key]; bins=sorted({int(n['start']//4)*4. for n in notes})
                monitor=[bins[i] for i in sorted(set(np.linspace(0,len(bins)-1,min(8,len(bins))).astype(int)))]
                c['monitor_offsets_s']=monitor; c['state']='training'
                rng=np.random.default_rng(4400+index); mean=initial.copy(); sigma=(HIGH-LOW)*.15
                best=initial.copy(); best_value=-1e9; pending=[]; covered=set()
                def measure(theta):
                    rr=list(pool.map(job,[(key,theta,[x],train_end) for x in monitor]))
                    c['evaluation_steps']+=sum(r['physics_steps'] for r in rr)
                    c['solver_warnings']+=sum(r.get('solver_warnings',0) for r in rr)
                    if any(r.get('cancelled') for r in rr): return None
                    nt=sum(r['metric']['target_notes'] for r in rr); na=sum(r['metric']['actual_notes'] for r in rr); tp=sum(r['metric']['matched'] for r in rr)
                    p=tp/na if na else 0; rec=tp/nt if nt else 0
                    return dict(precision=p,recall=rec,f1=2*p*rec/(p+rec) if p+rec else 0,matched=tp,target_notes=nt,actual_notes=na,solver_warnings=sum(r['solver_warnings'] for r in rr))
                vm=measure(best)
                if vm:
                    c['initial_validation']=vm; c['validation']=vm; best_value=vm['f1'] if not vm['solver_warnings'] else -1e9
                    c['history'].append(dict(wall_s=time.monotonic()-start,generation=0,metric=vm))
                while time.monotonic()<train_end and not stopped():
                    if not pending: pending=list(rng.permutation(bins))
                    offset=float(pending.pop()); pop=np.clip(rng.normal(mean,sigma,(8,len(mean))),LOW,HIGH)
                    pop[0]=mean; pop[1]=best
                    rr=list(pool.map(job,[(key,t,[offset],train_end) for t in pop]))
                    c['training_steps']+=sum(r['physics_steps'] for r in rr)
                    c['solver_warnings']+=sum(r.get('solver_warnings',0) for r in rr)
                    good=[i for i,r in enumerate(rr) if not r.get('cancelled') and not r['solver_warnings']]
                    if len(good)<3: break
                    covered.update(n['id'] for n in notes if offset<=n['start']<offset+4)
                    c['covered_note_ids']=sorted(covered)
                    elite=sorted(good,key=lambda i:rr[i]['reward'],reverse=True)[:3]
                    mean=.4*mean+.6*pop[elite].mean(0); sigma=np.maximum((HIGH-LOW)*.03,.4*sigma+.6*pop[elite].std(0))
                    c['generation']+=1
                    if c['generation']%5==0:
                        vm=measure(mean)
                        if vm:
                            c['validation']=vm
                            if not vm['solver_warnings'] and vm['f1']>best_value:
                                best_value=vm['f1'];best=mean.copy();c['parameters']=best.tolist()
                            c['history'].append(dict(wall_s=time.monotonic()-start,generation=c['generation'],metric=vm))
                    c['elapsed_s']=time.monotonic()-song_start
                    save('training',f"{key}: thế hệ {c['generation']}; đã luyện {len(covered)}/{len(notes)} nốt; không dừng theo precision.")
                c['state']='exporting'; save('exporting',f'{key}: đánh giá checkpoint cố định và ghi replay toàn bài.')
                # Full-song baseline and selected replay never affect checkpoint selection.
                for label,theta,record in [('baseline',initial,False),('trained',best,True)]:
                    try:
                        value=E.rollout(theta,notes,duration,record=record,cancel=lambda:time.monotonic()>=deadline)
                    except InterruptedError:
                        c['evaluation_steps']+=E.last_steps;c[label+'_incomplete']=True;break
                    r,frames=value if record else (value,None)
                    c['evaluation_steps']+=r['physics_steps'];c['solver_warnings']+=r['solver_warnings']
                    c[label+'_full_song']=brief(r['metrics'][2])
                    if record:
                        r.update(piece=key,diagnostic=True,practice_run_id=rid,evaluation_scope=config['evaluation_scope'])
                        frames.tofile(out/f'{key}.bin');r['replay_sha256']=sha(out/f'{key}.bin');atomic_json(out/f'{key}.json',r)
                        c['test']=brief(r['metrics'][2])
                        manifest['items'].append(dict(piece=key,metric=c['test'],physics_steps=r['physics_steps']))
                        atomic_json(folder/'replay_manifest.json',manifest)
                c['elapsed_s']=time.monotonic()-song_start
                c['state']='completed' if 'trained_full_song' in c else 'incomplete'
                save('training',f'{key}: đã kết thúc lượt luyện và đánh giá.')
        state='stopped' if stopped() else ('completed' if all(c['state']=='completed' for c in cells) else 'incomplete')
        save(state,'Đã kết thúc ngân sách. Xem P/R/F1 toàn bài; không áp dụng ngưỡng đạt.')
        atomic_json(ROOT/'results'/f'{rid}.json',dict(config=config,status=status,manifest=manifest))
        return folder
    except BaseException as ex:
        save('failed',repr(ex));raise

if __name__=='__main__':
    multiprocessing.freeze_support();p=argparse.ArgumentParser();p.add_argument('--minutes',type=float,default=120);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    print(run(a.minutes,a.workers),flush=True)
