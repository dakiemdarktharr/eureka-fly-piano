"""100-target mechanical diagnostics, not biological learning claims."""
import concurrent.futures,json,time
import numpy as np
from engine import Engine,INITIAL,brief
from v4_paths import ROOT,read_json,atomic_json

class Probe(Engine):
 def motor_gate(self,net,amp,theta):
  return super().motor_gate(net,amp,theta) if self.gate_value is None else np.full(6,self.gate_value)

def run(case):
 name,gate,source,extension=case;e=Probe();e.gate_value=gate
 t=np.r_[read_json(ROOT/'checkpoints/v4b_primary.json')['parameters'],np.zeros(6)] if source else INITIAL.copy()
 if extension is not None:t[30:36]=extension
 n,d=e.synthetic(82001,count=100);start=time.monotonic();r=e.rollout(t,n,d)
 return dict(name=name,metric=brief(r['metrics'][2]),warnings=r['solver_warnings'],wall_s=time.monotonic()-start,parameters=t.tolist(),gate=gate)

if __name__=='__main__':
 cases=[('legacy',None,True,None),('fixed_full_seed',1.,True,None),('fixed_full_neutral',1.,False,0.),('fixed_half_neutral',.5,False,0.)]
 with concurrent.futures.ProcessPoolExecutor(4) as pool:results=list(pool.map(run,cases))
 atomic_json(ROOT/'research/decoder_probe.json',dict(seed=82001,count=100,scope='Calibration-only data, never final test. Constant gates are engineered diagnostic controls.',results=results));print(json.dumps(results))
