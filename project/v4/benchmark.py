"""Paired active-contact benchmark; end-to-end and exact-state parity."""
import argparse,time,concurrent.futures,multiprocessing
import numpy as np
from engine import Engine,INITIAL
from v4_paths import ROOT,atomic_json
E=None
def init():
    global E
    E=Engine()
def job(seed):
    notes,d=E.synthetic(seed,count=3);r=E.rollout(INITIAL,notes,d)
    return {'steps':r['physics_steps'],'warnings':r['solver_warnings']}
def main():
    e=Engine();notes,d=e.synthetic(1337,count=3);rows=[];outputs=[]
    for batched in [False,True,False,True,False,True]:
        t=time.perf_counter();r=e.rollout(INITIAL,notes,d,batched=batched);elapsed=time.perf_counter()-t
        rows.append(dict(batched=batched,wall_s=elapsed,steps=r['physics_steps'],rtf=r['physics_seconds']/elapsed));outputs.append(r)
    parity=max(float(np.max(np.abs(np.array(outputs[0]['final_qpos'])-o['final_qpos']))) for o in outputs)
    parallel=[]
    for workers in [1,2,3,4]:
        with concurrent.futures.ProcessPoolExecutor(workers,mp_context=multiprocessing.get_context('spawn'),initializer=init) as pool:
            list(pool.map(job,range(workers))) # explicit startup warmup excluded
            start=time.perf_counter();rr=list(pool.map(job,range(12)));wall=time.perf_counter()-start
            steps=sum(r['steps'] for r in rr);parallel.append(dict(workers=workers,wall_s=wall,steps=steps,aggregate_rtf=steps*.0002/wall,warnings=sum(r['warnings'] for r in rr)))
    out=dict(mujoco=__import__('mujoco').__version__,dt=.0002,control_dt=.002,rows=rows,parallel=parallel,max_abs_qpos_difference=parity,events_identical=all(o['actual']==outputs[0]['actual'] for o in outputs),target_rtf=8766,scope='synthetic active contact; startup excluded only from worker throughput; not training result')
    atomic_json(ROOT/'research/cpu_benchmark.json',out);print(out,flush=True)
if __name__=='__main__':multiprocessing.freeze_support();main()
