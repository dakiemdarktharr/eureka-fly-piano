"""Validate the completed campaign and replay without further learning."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from v4_paths import ROOT,PROJECT,STATE,read_json,atomic_json
from train import skill_pass,sequence_pass
def main(run_id):
    folder=STATE/'runs'/run_id;s=read_json(folder/'status.json');cfg=read_json(folder/'config.json')
    assert s['state']=='completed'
    checks={}
    checks['source_hashes']=all(hashlib.sha256((PROJECT/p).read_bytes()).hexdigest()==h for p,h in cfg['hashes'].items())
    assert checks['source_hashes'],'Source files changed during campaign'
    steps=sum(c['training_steps']+c['evaluation_steps'] for c in s['cells']);assert steps==s['physics_steps']
    assert abs(s['aggregate_simulated_s']-steps*cfg['dt'])<1e-8
    checks['step_ledger']=True
    for c in s['cells']:
        assert c.get('test') is not None,'Incomplete held-out test'
        m=c['test'];tp=m['matched'];assert tp<=min(m['target_notes'],m['actual_notes'])
        assert c['skill_pass']==skill_pass(m)
        assert len(c['parameters'])==49
        if c['variant']=='frozen':assert not any(c['parameters'][:24])
        if c['sequence_pass']:assert sequence_pass(c['sequence_test'])
    checks['metrics_and_gates']=True
    pilot=read_json(ROOT/'results/20260918T055453.json')['status'];combined=s['elapsed_s']+pilot['elapsed_s'];assert combined<=3600
    checks['shared_hour_budget']=dict(seconds=combined,cap=3600)
    manifest=read_json(folder/'replay_manifest.json');primary=next(c for c in s['cells'] if c['variant']=='adaptive' and c['seed']==0)
    assert manifest['qualified_song_demonstration']==(primary['skill_pass'] and primary['sequence_pass'])
    for item in manifest['items']:
        key=item['piece'];r=read_json(folder/f'replays/{key}.json');p=folder/f'replays/{key}.bin';f=np.fromfile(p,dtype='<f4')
        assert f.size==r['frame_count']*r['stride'] and np.isfinite(f).all()
        assert hashlib.sha256(p.read_bytes()).hexdigest()==r['replay_sha256']
        assert r['solver_warnings']==0
    checks['replay_integrity']=True
    result=dict(run_id=run_id,checks=checks,qualified_demo=manifest['qualified_song_demonstration'],note='Replay physics and benchmark are separate from the learner budget; no additional optimization in this audit')
    atomic_json(ROOT/'qa/artifact_audit.json',result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');main(p.parse_args().run)
