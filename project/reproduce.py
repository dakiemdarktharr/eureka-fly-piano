"""Cross-platform entry point. PowerShell wrappers create/verify the environment."""
from pathlib import Path
import sys,json,argparse,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from experiments.run import run
from experiments.registry import registry,write_registry
from connectome.prepare import prepare,dump,sha

def core():
    if not (ROOT/'connectome/weights.npy').exists():prepare()
    subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_*.py'],check=True,cwd=ROOT)
    rows=[];root=ROOT/'data/core/runs'
    for rid in ['A1_tonic_full_s00','A1_tonic_no_cpg_s00','A1_tonic_no_dn_s00','B1_novel_full_s00']:
        c=next(c for c in registry() if c['run_id']==rid);m=run(c,root);rows.append({'id':rid,'metrics':m})
    assert .2<rows[0]['metrics']['motor_rhythm_power']<=1
    assert rows[1]['metrics']['motor_rhythm_power']==rows[2]['metrics']['motor_rhythm_power']==0
    assert 0<=rows[3]['metrics']['key_accuracy']<=1
    # Deterministic four-key vertical slice, kept outside primary results.
    c=next(c for c in registry([42]) if c['experiment_id']=='B1' and c['variant']=='full')
    c.update(run_id='C0_four_key_s42',nkeys=4,duration=4.)
    run(c,root);p=root/c['run_id']/'telemetry.npz';first=sha(p);run(c,root);assert sha(p)==first
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    z=np.load(root/'A1_tonic_full_s00/telemetry.npz');fig,ax=plt.subplots(figsize=(8,3));ax.plot(z['time'],z['rates'].mean(1));ax.set(xlabel='Time (s)',ylabel='Mean modeled rate (Hz)',title='Core check: tonic drive / full / seed 0');fig.tight_layout();out=ROOT/'paper/figures';out.mkdir(parents=True,exist_ok=True);fig.savefig(out/'core_check.png',dpi=150);plt.close(fig);z.close()
    from visualization.video import render
    render(['B1_novel_full_s00'],'core_replay',run_root=root)
    dump(ROOT/'data/core/checks.json',{'status':'pass','checks':['unit tests','tonic rhythm','CPG and DN negative controls','contact range','four-key bitwise determinism','figure','video'],'runs':rows})
    print('Core reproduction passed',flush=True)

def all_runs():
    if not (ROOT/'connectome/weights.npy').exists():prepare()
    write_registry(ROOT/'experiments/registry.json')
    for c in registry():run(c);print(c['run_id'],flush=True)
    from analysis.summarize import summarize
    from analysis.extended import calculate
    from visualization.video import render
    summarize();calculate();render(['B1_novel_full_s00'],'controlled_motor_tests');render(['B1_novel_full_s00','B1_novel_no_cpg_s00','B1_novel_direct_s00'],'ablation_comparison')
    from paper.build import build
    build()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['core','all'],default='core',nargs='?');a=p.parse_args();core() if a.mode=='core' else all_runs()
