"""Derived metrics from immutable telemetry; no simulation changes."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
from scipy.signal import hilbert,periodogram
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulation.model import ROOT

def calculate():
    table=pd.read_csv(ROOT/'connectome/neurons.csv');rows=[]
    groups=[np.flatnonzero((table.kind=='MN')&(table.leg==i)) for i in range(6)]
    for path in sorted((ROOT/'data/runs').glob('*/telemetry.npz')):
        m=json.loads((path.parent/'metadata.json').read_text());z=np.load(path);t=z['time'];r=z['rates'];q=z['q']
        # Participation ratio = tr(C)^2/tr(C^2), avoiding unstable rank thresholds.
        x=r[::10].astype(float);x-=x.mean(0);cov=x.T@x/max(1,len(x)-1)
        dimensionality=float(np.trace(cov)**2/(np.sum(cov*cov)+1e-20))
        leg=np.array([r[:,g].sum(1) for g in groups]).T
        active=leg[t>4].std(0)>.1
        phase=np.angle(hilbert(leg-leg.mean(0),axis=0));plv=[]
        for i in range(6):
            for j in range(i+1,6):
                if active[i] and active[j]:plv.append(abs(np.exp(1j*(phase[t>4,i]-phase[t>4,j])).mean()))
        def freq(mask):
            ff,p=periodogram(leg[mask],fs=1/m['dt'],axis=0);band=(ff>=1)&(ff<=40)
            ac=leg[mask].std(0)>.1
            return float(ff[band][p[band].argmax(0)][ac].mean()) if ac.any() else None
        pre=freq((t>2)&(t<3.8));post=freq((t>5)&(t<7.8))
        contacts=m['contacts'];meanr=r.mean(0)
        row={'run_id':m['run_id'],'effective_state_dimension':dimensionality,'interleg_plv':float(np.mean(plv)) if plv else None,
          'active_leg_count':int(active.sum()),'frequency_pre_hz':pre,'frequency_post_hz':post,
          'frequency_change_hz':post-pre if pre is not None and post is not None else None,
          'dn_mean_hz':float(meanr[table.kind=='DN'].mean()),'cpg_mean_hz':float(meanr[table.kind=='CPG'].mean()),
          'contact_limb_count':len(set(c['limb'] for c in contacts)),
          'contact_force_peak':float(z['force'].max()),
          'scope':'descriptive model-only metrics; phase absent for inactive limbs'}
        rows.append(row);z.close()
    out=ROOT/'paper/tables/extended_metrics.csv';pd.DataFrame(rows).to_csv(out,index=False);print(f'Extended metrics: {len(rows)} runs')
if __name__=='__main__':calculate()
