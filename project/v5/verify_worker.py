import concurrent.futures,multiprocessing,time,json
import numpy as np
from train_hundred import init,job
from v4_paths import ROOT,read_json,atomic_json

if __name__=='__main__':
 multiprocessing.freeze_support();theta=np.r_[read_json(ROOT/'checkpoints/v4b_primary.json')['parameters'],np.zeros(6)]
 with concurrent.futures.ProcessPoolExecutor(2,mp_context=multiprocessing.get_context('spawn'),initializer=init) as pool:
  results=list(pool.map(job,[(key,theta,[0],time.monotonic()+180) for key in ['merry','pool']]))
 for r in results:
  assert not r.get('cancelled');assert r['metric']['target_notes']==100;assert not r['solver_warnings']
 atomic_json(ROOT/'qa/worker_check.json',dict(songs=['merry','pool'],results=results));print(json.dumps(results))
