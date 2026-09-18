"""Resumable CEM, honest compute clocks and validation-gated stopping."""
import argparse,datetime,hashlib,json,os,time,traceback
import numpy as np
from paths import RUNS,V2,PROJECT,atomic_json,read_json
from engine import Engine,INITIAL,LOW,HIGH,NAMES,clips_for,partition,scores

def fingerprint():return {k:hashlib.sha256((V2/f'data/{k}_score.json').read_bytes()).hexdigest() for k in ['merry','pool']}
def plant_fingerprint():
 paths=[PROJECT/'connectome/weights.npy',PROJECT/'connectome/neurons.csv',V2/'data/ik_cache.npz',V2/'assets/fly_model/piano_fly.xml']
 return {str(p.relative_to(PROJECT)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def passes(results,threshold=.85):
 return all(results[k]['precision']>threshold and results[k]['recall']>=threshold and results[k]['f1']>=threshold and results[k]['target_notes']>0 and results[k]['actual_notes']>0 and results[k]['solver_warnings']==0 for k in ['merry','pool'])
def create_run(minutes=15,seed=0,population=6,clip_seconds=6):
 if not 1<=minutes<=1440 or not 4<=population<=16 or not 2<=clip_seconds<=30:raise ValueError('Invalid budget/population/clip length')
 run_id=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+f'-s{seed}-{os.urandom(2).hex()}'
 folder=RUNS/run_id;folder.mkdir(parents=True)
 config={'schema':1,'run_id':run_id,'minutes':minutes,'seed':seed,'population':population,'clip_seconds':clip_seconds,'threshold':.85,'consecutive_passes':3,'score_hashes':fingerprint(),'plant_hashes':plant_fingerprint(),'split':{k:partition(s) for k,s in scores().items()},'algorithm':'diagonal CEM, 16 readout parameters; frozen connectome','created':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 atomic_json(folder/'config.json',config);atomic_json(folder/'status.json',{'run_id':run_id,'state':'queued','target_met':False,'message':'Đang chuẩn bị huấn luyện','learning_seconds':0,'checkpoints':[]});return run_id

def train(run_id,additional_minutes=None):
 folder=RUNS/run_id;config=read_json(folder/'config.json')
 if fingerprint()!=config['score_hashes']:raise ValueError('Score hashes changed; cannot resume this run')
 if config.get('plant_hashes') and plant_fingerprint()!=config['plant_hashes']:raise ValueError('Plant hashes changed; create a new run')
 if (folder/'pause.request').exists():(folder/'pause.request').unlink()
 engine=Engine(config['seed']);rng=np.random.default_rng(config['seed']);pieces=engine.pieces
 monitor=clips_for(pieces,'train',config['clip_seconds'],count=1)
 validation=clips_for(pieces,'validation',config['clip_seconds'],count=2)
 test=clips_for(pieces,'test',config['clip_seconds'],count=2)
 if (folder/'optimizer.json').exists():
  o=read_json(folder/'optimizer.json');rng.bit_generator.state=o['rng_state'];o['budget_seconds']=o['learning_seconds']+60*(additional_minutes or config['minutes'])
 else:
  o={'generation':0,'mean':((INITIAL-LOW)/(HIGH-LOW)).tolist(),'sigma':[.23]*16,'best_theta':INITIAL.tolist(),'best_monitor':None,'rng_state':rng.bit_generator.state,'learning_seconds':0.,'evaluation_seconds':0.,'physics_steps':0,'candidate_evaluations':0,'budget_seconds':config['minutes']*60,'pending':None,'checkpoints':[],'success_streak':0,'target_met':False,'wall_seconds':0.}
 started=time.perf_counter();prior_wall=o['wall_seconds'];pause=lambda:(folder/'pause.request').exists()
 def save(state='training',message='Đang tối ưu controller'):
  o['rng_state']=rng.bit_generator.state;o['wall_seconds']=prior_wall+time.perf_counter()-started
  atomic_json(folder/'optimizer.json',o)
  atomic_json(folder/'status.json',{'run_id':run_id,'state':state,'message':message,'pid':os.getpid(),'target_met':o['target_met'],'learning_seconds':o['learning_seconds'],'evaluation_seconds':o['evaluation_seconds'],'wall_seconds':o['wall_seconds'],'budget_seconds':o['budget_seconds'],'physics_steps':o['physics_steps'],'candidate_evaluations':o['candidate_evaluations'],'generation':o['generation'],'best_parameters':dict(zip(NAMES,o['best_theta'])),'checkpoints':o['checkpoints'],'success_streak':o['success_streak'],'config':config})
 def evaluate(theta,clips,learning=False):
  before=time.perf_counter();before_steps=engine.total_steps
  try:return engine.evaluate(theta,clips,cancel=pause)
  finally:
   o['learning_seconds' if learning else 'evaluation_seconds']+=time.perf_counter()-before;o['physics_steps']+=engine.total_steps-before_steps
 def checkpoint(label):
  save('evaluating',f'Đánh giá checkpoint {label}; không cập nhật từ validation')
  val=evaluate(o['best_theta'],validation)
  passed=passes(val,config['threshold']);o['success_streak']=o['success_streak']+1 if passed else 0;o['target_met']=o['success_streak']>=config['consecutive_passes']
  cp={'index':len(o['checkpoints']),'label':label,'learning_seconds':o['learning_seconds'],'evaluation_seconds':o['evaluation_seconds'],'physics_steps':o['physics_steps'],'candidate_evaluations':o['candidate_evaluations'],'generation':o['generation'],'parameters':o['best_theta'],'train':o['best_monitor'],'validation':val,'threshold_passed':passed,'target_met':o['target_met'],'score_hashes':config['score_hashes']}
  atomic_json(folder/f"checkpoint_{cp['index']:03}.json",cp);o['checkpoints'].append(cp);save();print(f"CHECKPOINT {label}: train F1 {cp['train']['macro_f1']:.4f}, validation F1 {val['macro_f1']:.4f}, success={o['target_met']}",flush=True)
 def due():
  elapsed=o['learning_seconds'];done={c['label'] for c in o['checkpoints']};milestones=[60,300,900]+list(range(1200,int(o['budget_seconds'])+301,300))
  for seconds in milestones:
   label=f'{seconds//60} phút'
   if elapsed>=seconds and label not in done:checkpoint(label)
 save()
 try:
  if o['best_monitor'] is None:o['best_monitor']=evaluate(INITIAL,monitor);checkpoint('0 phút')
  while o['learning_seconds']<o['budget_seconds'] and not o['target_met']:
   if pause():raise InterruptedError('Pause requested')
   if o['pending'] is None:
    clips=clips_for(pieces,'train',config['clip_seconds'],count=1,rng=rng)
    normalized=np.clip(rng.normal(o['mean'],o['sigma'],size=(config['population'],16)),0,1)
    candidates=[o['best_theta']]+[(LOW+u*(HIGH-LOW)).tolist() for u in normalized]
    o['pending']={'clips':[list(c) for c in clips],'candidates':candidates,'results':[]};save()
   pending=o['pending']
   while len(pending['results'])<len(pending['candidates']):
    i=len(pending['results']);save(message=f"Thế hệ {o['generation']+1}, ứng viên {i+1}/{len(pending['candidates'])}")
    result=evaluate(pending['candidates'][i],pending['clips'],learning=True);pending['results'].append(result);o['candidate_evaluations']+=1;save();due()
    if o['learning_seconds']>=o['budget_seconds'] or o['target_met']:break
   if len(pending['results'])<len(pending['candidates']):break
   order=np.argsort([r['macro_f1'] for r in pending['results']])[::-1];winner=pending['candidates'][int(order[0])]
   trial=evaluate(winner,monitor,learning=True)
   if trial['macro_f1']>o['best_monitor']['macro_f1']+1e-12:o['best_theta']=winner;o['best_monitor']=trial
   elite=np.array([pending['candidates'][int(i)] for i in order[:max(2,config['population']//3)]])
   elite=(elite-LOW)/(HIGH-LOW);o['mean']=(.7*elite.mean(0)+.3*np.array(o['mean'])).tolist();o['sigma']=np.maximum(.035,.7*elite.std(0)+.3*np.array(o['sigma'])).tolist()
   o['generation']+=1;o['pending']=None;save();due()
  if not o['checkpoints'] or o['checkpoints'][-1]['parameters']!=o['best_theta'] or abs(o['checkpoints'][-1]['learning_seconds']-o['learning_seconds'])>1:checkpoint('kết thúc lượt')
  # Stopping at a budget does not count as success, and the final ad-hoc
  # checkpoint cannot manufacture an extra scheduled success streak.
  scheduled=[c for c in o['checkpoints'] if c['label']!='kết thúc lượt']
  o['success_streak']=0
  for c in reversed(scheduled):
   if not c['threshold_passed']:break
   o['success_streak']+=1
  o['target_met']=o['success_streak']>=config['consecutive_passes']
  save('testing','Đánh giá phần test sau khi khóa checkpoint; không dùng để tối ưu')
  heldout=evaluate(o['best_theta'],test);history=read_json(folder/'test_history.json') if (folder/'test_history.json').exists() else []
  history.append({'evaluation':len(history)+1,'parameters':o['best_theta'],'results':heldout,'scope':'within-piece holdout; repeated evaluation after resume is exploratory' if history else 'first held-out evaluation after checkpoint selection'})
  atomic_json(folder/'test_history.json',history);save('target_met' if o['target_met'] else 'budget_exhausted','Đạt tiêu chí validation; xem test riêng' if o['target_met'] else 'Hết ngân sách lượt này, chưa đạt 85%; checkpoint đã lưu để tiếp tục')
 except InterruptedError:
  save('paused','Đã tạm dừng và lưu trạng thái; ứng viên dở dang sẽ chạy lại khi tiếp tục')
 except Exception as e:
  save('failed',str(e));(folder/'error.txt').write_text(traceback.format_exc(),encoding='utf8');raise
 return read_json(folder/'status.json')

def export_replays(run_id):
 folder=RUNS/run_id;o=read_json(folder/'optimizer.json');config=read_json(folder/'config.json');engine=Engine(config['seed']);out=folder/'replays';out.mkdir(exist_ok=True)
 for key,s in engine.pieces.items():
  result,array=engine.rollout(o['best_theta'],key,0,s['duration']+1,record=True);result.update(run_id=run_id,score_sha256=config['score_hashes'][key],checkpoint_learning_seconds=o['learning_seconds'],evaluation_scope='full-song demonstration combines training and held-out regions; not a fresh test')
  path=out/f'{key}_trained.bin';array.tofile(path);result['replay_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();atomic_json(out/f'{key}_trained.json',result);print('REPLAY',key,result['metrics'][2]['precision'],flush=True)
 atomic_json(RUNS.parent/'active_replay.json',{'run_id':run_id})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run');p.add_argument('--minutes',type=float,default=15);p.add_argument('--seed',type=int,default=0);p.add_argument('--resume',action='store_true');p.add_argument('--export',action='store_true');a=p.parse_args()
 rid=a.run or create_run(a.minutes,a.seed)
 if a.export:export_replays(rid)
 else:print('RUN',rid,flush=True);train(rid,a.minutes if a.resume else None)
