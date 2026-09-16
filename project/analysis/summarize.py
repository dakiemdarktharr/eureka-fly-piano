from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulation.model import ROOT
from connectome.prepare import dump

METRICS=['motor_rhythm_power','motor_frequency_hz','oscillating_mn_fraction','key_accuracy','precision','timing_mae_s','timing_jitter_s','misses','extra_contacts','energy_proxy','joint_velocity_rms']
def bootstrap(x,seed=9901):
    x=np.asarray(x,float);x=x[np.isfinite(x)]
    if len(x)==0:return [None,None]
    rng=np.random.default_rng(seed);b=x[rng.integers(0,len(x),(4000,len(x)))].mean(1)
    return np.quantile(b,[.025,.975]).tolist()
def summarize():
    rows=[]
    for p in sorted((ROOT/'data/runs').glob('*/metrics.json')):
        meta=json.loads((p.parent/'metadata.json').read_text());m=json.loads(p.read_text())
        meta['sequence_id']=hashlib.sha256(json.dumps(meta['events'],sort_keys=True).encode()).hexdigest()[:16] if meta['events'] else 'tonic'
        rows.append({**{k:meta[k] for k in ['run_id','experiment_id','condition','variant','seed','sequence_id']},**{k:m.get(k) for k in METRICS}})
    df=pd.DataFrame(rows);out=ROOT/'paper/tables';out.mkdir(parents=True,exist_ok=True);df.to_csv(out/'per_run.csv',index=False)
    results=[];tests=[]
    for (exp,cond,var),g in df.groupby(['experiment_id','condition','variant'],sort=True):
        for metric in METRICS:
            x=g[metric].dropna().to_numpy(float);ci=bootstrap(x)
            results.append(dict(experiment_id=exp,condition=cond,variant=var,metric=metric,n=len(x),n_seeds=g.seed.nunique(),n_sequences=(0 if exp=='A1' else g.sequence_id.nunique()),n_connectome_instances=1,
             mean=float(x.mean()) if len(x) else None,median=float(np.median(x)) if len(x) else None,sd=float(x.std(ddof=1)) if len(x)>1 else None,ci_low=ci[0],ci_high=ci[1]))
    for (exp,cond),g in df.groupby(['experiment_id','condition']):
        full=g[g.variant=='full'].set_index('seed')
        for var,sub in g[g.variant!='full'].groupby('variant'):
            sub=sub.set_index('seed')
            for metric in ['motor_rhythm_power','key_accuracy','timing_mae_s']:
                pair=pd.concat([full[metric].rename('a'),sub[metric].rename('b')],axis=1).dropna()
                if len(pair)<2:continue
                delta=(pair.a-pair.b).to_numpy(float);sd=delta.std(ddof=1)
                p=float(ttest_rel(pair.a,pair.b).pvalue) if sd>1e-12 else (1. if abs(delta.mean())<1e-12 else None)
                ci=bootstrap(delta)
                tests.append(dict(experiment_id=exp,condition=cond,comparison='full - '+var,metric=metric,n_pairs=len(pair),mean_difference=float(delta.mean()),ci_low=ci[0],ci_high=ci[1],cohens_dz=float(delta.mean()/sd) if sd>1e-12 else None,p_raw=p,test='paired two-sided t; descriptive at small n',p_holm=None))
    ix=sorted([i for i,t in enumerate(tests) if t['p_raw'] is not None],key=lambda i:tests[i]['p_raw']);last=0
    for rank,i in enumerate(ix):last=max(last,min(1,(len(ix)-rank)*tests[i]['p_raw']));tests[i]['p_holm']=last
    pd.DataFrame(results).to_csv(out/'summary.csv',index=False);pd.DataFrame(tests).to_csv(out/'contrasts.csv',index=False)
    dump(out/'summary.json',results);dump(out/'contrasts.json',tests)
    representations=[]
    for seed in sorted(df.seed.unique()):
        base=ROOT/f'data/runs/B1_novel_full_s{seed:02d}/telemetry.npz'
        if not base.exists():continue
        with np.load(base) as z:task=z['task'].copy();q=z['q'].copy();rates=z['rates'].copy()
        for condition in ['mirrored','shifted','spacing','height']:
            path=ROOT/f'data/runs/B2_{condition}_full_s{seed:02d}/telemetry.npz'
            if not path.exists():continue
            with np.load(path) as z:
                representations.append(dict(seed=int(seed),context=condition,task_state_rms=float(np.sqrt(np.mean((task-z['task'])**2))),vnc_rate_rms=float(np.sqrt(np.mean((rates-z['rates'])**2))),joint_rms=float(np.sqrt(np.mean((q-z['q'])**2))),interpretation='task invariance is imposed by context-free engineering, not learned'))
    pd.DataFrame(representations).to_csv(out/'representations.csv',index=False)
    figs=ROOT/'paper/figures';figs.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(11,4.5),constrained_layout=True)
    rng=np.random.default_rng(11)
    for ax,exp,metric,title in [(axs[0],'A1','motor_rhythm_power','Tonic descending drive'),(axs[1],'B1','key_accuracy','Novel synthetic sequence execution')]:
        g=df[df.experiment_id==exp];vs=list(g.variant.unique())
        for i,v in enumerate(vs):
            x=g[g.variant==v][metric].dropna().to_numpy(float)
            if not len(x):continue
            ci=bootstrap(x);ax.scatter(i+rng.uniform(-.12,.12,len(x)),x,s=12,alpha=.7,color='#247c91')
            ax.plot([i-.18,i+.18],[x.mean()]*2,color='#ad4939',lw=2);ax.vlines(i,*ci,color='#ad4939')
        ax.set_xticks(range(len(vs)),vs,rotation=65,ha='right',fontsize=7);ax.set_ylim(-.04,1.04);ax.set_title(title);ax.set_ylabel(metric.replace('_',' '))
    manifest=json.loads((ROOT/'connectome_manifest.json').read_text())
    fig.suptitle('Model tests | 412 measured neurons | dots: independent parameter seeds',fontsize=12)
    fig.savefig(figs/'core_results.png',dpi=180);fig.savefig(figs/'core_results.svg');plt.close(fig)
    trace=ROOT/'data/runs/A1_tonic_full_s00/telemetry.npz'
    if trace.exists():
        z=np.load(trace);table=pd.read_csv(ROOT/'connectome/neurons.csv');sel=table.bodyId.isin([10093,10707,11751,13905]).to_numpy();fig,ax=plt.subplots(figsize=(10,3.3),constrained_layout=True)
        for i in np.flatnonzero(sel):ax.plot(z['time'],z['rates'][:,i],label=str(table.iloc[i].bodyId)+' '+table.iloc[i].type,lw=.9)
        ax.set(xlim=(1,2),xlabel='Time (s)',ylabel='Modeled rate (Hz)',title='A1 tonic / full / seed 0');ax.legend(fontsize=7,ncol=2);fig.savefig(figs/'neural_trace.png',dpi=180);fig.savefig(figs/'neural_trace.svg');plt.close(fig)
    figure_runs=[json.loads(p.read_text()) for p in (ROOT/'data/runs').glob('*/metadata.json') if p.parent.name.startswith(('A1_','B1_'))]
    dump(figs/'run_provenance.json',[{k:m[k] for k in ['run_id','variant','seed','git_commit','dataset_version','config_sha256','graph_sha256']} for m in figure_runs])
    dump(figs/'provenance.json',{'source':'paper/tables/per_run.csv and telemetry','experiments':['A1','B1'],'variants':sorted(df.variant.unique().tolist()),'seeds':sorted(map(int,df.seed.unique())), 'dataset_version':manifest['dataset_version'],'graph_sha256':manifest['graph_sha256'],'rendering':'fixed y limits; no per-frame normalization'})
    print(f'Summarized {len(df)} runs; {len(tests)} paired contrasts',flush=True)
    return df
if __name__=='__main__':summarize()
