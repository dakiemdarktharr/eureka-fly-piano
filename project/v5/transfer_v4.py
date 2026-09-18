"""One-off, audited warm-start transfer; never claims exact optimizer resume."""
from pathlib import Path
import hashlib,json,shutil
from v4_paths import ROOT,PROJECT,atomic_json,read_json

def main():
 old_state=PROJECT/'v4/dist/FlyPianoLabV4/runtime';rid=read_json(old_state/'latest.json')['run_id'];source=old_state/'runs'/rid;s=read_json(source/'status.json')
 if s['state'] not in ['stopped','completed','incomplete']:raise RuntimeError(f"Wait for graceful export: {s['state']}")
 backup=PROJECT/'v4/runtime/runs'/rid;shutil.copytree(source,backup,dirs_exist_ok=True)
 for p in source.rglob('*'):
  if p.is_file():assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((backup/p.relative_to(source)).read_bytes()).digest()
 warm={}
 for cell in s['cells']:
  warm[cell['song']]=dict(parameters=cell['parameters']+[0.]*6,consumed_s=cell.get('elapsed_s',0),source_run=rid,source_generation=cell['generation'],source_status_sha256=hashlib.sha256((source/'status.json').read_bytes()).hexdigest(),transfer='Warm start only; reset optimizer for 100-target protocol')
 destination=ROOT/'dist/FlyPianoLabV5/runtime';assert not (destination/'latest.json').exists(),'Do not overwrite an existing v5 campaign'
 atomic_json(destination/'continuation.json',warm);shutil.copytree(ROOT/'runtime/preview',destination/'preview',dirs_exist_ok=True)
 atomic_json(ROOT/'results/transition.json',dict(prior_run=rid,prior_state=s['state'],prior_elapsed_s=s['elapsed_s'],remaining_seconds={k:max(0,7200-c['consumed_s']) for k,c in warm.items()},backup_verified=True,optimizer_resume=False))
 print(json.dumps(read_json(ROOT/'results/transition.json')))
if __name__=='__main__':main()
