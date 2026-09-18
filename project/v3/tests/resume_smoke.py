"""Opt-in real-physics pause/resume smoke; keeps runs separate from the paper."""
import os,sys,time,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['FLYPIANO_STATE']=str(ROOT/'qa/resume_state')
sys.path.insert(0,str(ROOT))
from train import create_run
from paths import RUNS,read_json
rid=create_run(1,123,population=4,clip_seconds=2);folder=RUNS/rid
def segment(action,minimum):
 with (folder/'smoke.log').open('ab') as log:
  proc=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--worker',rid,'--action',action,'--minutes','1'],stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
  deadline=time.monotonic()+180;sent=False
  while proc.poll() is None and time.monotonic()<deadline:
   s=read_json(folder/'status.json')
   if s.get('candidate_evaluations',0)>=minimum and not sent:(folder/'pause.request').write_text('pause');sent=True
   time.sleep(.2)
  if proc.poll() is None:proc.terminate();raise RuntimeError('Worker timeout')
  if proc.returncode:raise RuntimeError((folder/'smoke.log').read_text())
 s=read_json(folder/'status.json');assert s['state']=='paused',s
 return read_json(folder/'optimizer.json')
first=segment('train',1);assert first['pending'] and first['pending']['results']
second=segment('resume',first['candidate_evaluations']+1)
assert second['candidate_evaluations']>first['candidate_evaluations']
assert second['learning_seconds']>first['learning_seconds']
assert second['pending']['candidates']==first['pending']['candidates']
assert second['pending']['results'][0]==first['pending']['results'][0]
report={'run_id':rid,'passed':True,'first_candidates':first['candidate_evaluations'],'resumed_candidates':second['candidate_evaluations'],'same_pending_population':True,'retained_completed_candidate':True,'accumulated_compute':True,'scope':'real physics smoke, excluded from scientific campaign'}
(ROOT/'qa/resume_check.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
