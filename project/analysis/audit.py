"""Mechanical integrity checks on every registered run; fails on missing evidence."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulation.model import ROOT
from experiments.run import score_contacts
from connectome.prepare import sha,dump

def audit():
    reg=json.loads((ROOT/'experiments/registry.json').read_text());issues=[];checked=0
    for c in reg:
        p=ROOT/'data/runs'/c['run_id']
        if not (p/'telemetry.npz').exists():issues.append(c['run_id']+': missing telemetry');continue
        m=json.loads((p/'metadata.json').read_text());out=json.loads((p/'metrics.json').read_text())
        if sha(p/'telemetry.npz')!=m['telemetry_sha256']:issues.append(c['run_id']+': hash mismatch')
        expected=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
        if expected!=m['config_sha256']:issues.append(c['run_id']+': registered config mismatch')
        with np.load(p/'telemetry.npz') as z:
            if not all(np.isfinite(z[k]).all() for k in z.files):issues.append(c['run_id']+': nonfinite state')
            if z['rates'].shape!=(4000,412):issues.append(c['run_id']+': unexpected rate shape')
            if not np.allclose(np.diff(z['time']),c['dt'],rtol=0,atol=1e-12):issues.append(c['run_id']+': time grid')
            if np.any(z['force']<0):issues.append(c['run_id']+': tensile unilateral contact')
            for contact in m['contacts']:
                ix=round(contact['time']/c['dt']);leg=contact['limb']
                if z['actual'][ix,leg]!=contact['key'] or z['force'][ix,leg]<=.04:issues.append(c['run_id']+': contact not in raw telemetry')
        recomputed=score_contacts(m['events'],m['contacts'])
        for k in ['key_accuracy','misses','extra_contacts','timing_mae_s']:
            if recomputed[k]!=out[k]:issues.append(c['run_id']+': metric mismatch '+k)
        checked+=1
    report={'status':'pass' if not issues else 'fail','registered_runs':len(reg),'checked_runs':checked,'issues':issues,
      'checks':['complete registry coverage','all telemetry checksums','config hashes','finite neural/body arrays','fixed time grid','unilateral force','raw contact correspondence','independent contact metric recomputation'],
      'limits':'Does not validate biological assumptions, learning, data rights or numerical convergence.'}
    dump(ROOT/'docs/integrity_audit.json',report);print(json.dumps(report))
    if issues:raise SystemExit(1)
if __name__=='__main__':audit()
