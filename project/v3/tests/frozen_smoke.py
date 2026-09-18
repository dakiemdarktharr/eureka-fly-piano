"""Exercise the packaged app API and an actual packaged physics worker."""
import json,time,urllib.request
from pathlib import Path
BASE='http://127.0.0.1:8878';ROOT=Path(__file__).resolve().parents[1]
def get(path):return json.load(urllib.request.urlopen(BASE+path,timeout=10))
def post(path,value):
 req=urllib.request.Request(BASE+path,json.dumps(value).encode(),headers={'Content-Type':'application/json','X-FlyPiano-Token':get('/api/state')['csrf']},method='POST')
 return json.load(urllib.request.urlopen(req,timeout=20))
health=get('/api/health');assert health['ready'],health
rid=post('/api/train',{'minutes':1,'seed':321})['run_id']
def pause_after(n):
 deadline=time.monotonic()+180;sent=False
 while time.monotonic()<deadline:
  run=next(r for r in get('/api/state')['runs'] if r['run_id']==rid)
  if run['state'] in ['failed','interrupted']:raise RuntimeError(run)
  if run.get('candidate_evaluations',0)>=n and not sent:post('/api/pause',{'run_id':rid});sent=True
  if run['state']=='paused':return run
  time.sleep(.25)
 raise RuntimeError('Packaged worker timeout')
first=pause_after(1);post('/api/resume',{'run_id':rid,'minutes':1});second=pause_after(2)
assert second['candidate_evaluations']>first['candidate_evaluations']
report={'packaged_health':health,'run_id':rid,'real_worker_started':True,'pause_resume':True,'first_candidates':first['candidate_evaluations'],'resumed_candidates':second['candidate_evaluations'],'scope':'packaged Windows smoke, excluded from paper'}
(ROOT/'qa/frozen_check.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
