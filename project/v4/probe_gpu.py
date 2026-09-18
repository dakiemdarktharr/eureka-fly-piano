"""Capability and throughput probe; never counts as training or asserts parity."""
import os,time,json,traceback,argparse
from v4_paths import ROOT,atomic_json
from world import PianoWorld
import numpy as np
def main():
 p=argparse.ArgumentParser();p.add_argument('--worlds',type=int,default=16);a=p.parse_args()
 report={'worlds':a.worlds,'training':False,'passed':False};start=time.perf_counter()
 try:
  import warp as wp,mujoco_warp as mjw,mujoco as mj
  wp.init();report['warp_version']=wp.__version__;report['mujoco_version']=mj.__version__;report['device']=str(wp.get_device('cuda:0'))
  w=PianoWorld();report.update(nq=w.model.nq,nv=w.model.nv,ngeom=w.model.ngeom)
  with wp.ScopedDevice('cuda:0'):
   m=mjw.put_model(w.model);d=mjw.put_data(w.model,w.data,nworld=a.worlds,nconmax=64,njmax=512)
   wp.copy(d.ctrl,wp.array(np.tile(w.neutral_ctrl,(a.worlds,1)).astype(np.float32)))
   mjw.step(m,d);wp.synchronize();report['compile_and_setup_s']=time.perf_counter()-start
   with wp.ScopedCapture() as cap:
    for _ in range(10):mjw.step(m,d)
   t=time.perf_counter()
   for _ in range(100):wp.capture_launch(cap.graph)
   wp.synchronize();elapsed=time.perf_counter()-t
   q=d.qpos.numpy();report.update(passed=bool(np.isfinite(q).all()),benchmark_seconds=elapsed,steps=a.worlds*1000,steps_per_second=a.worlds*1000/elapsed,aggregate_realtime_factor=a.worlds*1000*w.model.opt.timestep/elapsed,scope='neutral-body capability probe; no contact/controller fidelity validation')
 except Exception as e:report.update(error=str(e),traceback=traceback.format_exc())
 report['total_seconds']=time.perf_counter()-start;atomic_json(ROOT/f'research/gpu_probe_{a.worlds}.json',report);print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
