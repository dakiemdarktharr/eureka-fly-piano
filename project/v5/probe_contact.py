import concurrent.futures,json,time
import numpy as np
from contact_ik import ContactEngine
from engine import Engine,INITIAL,brief
from v4_paths import ROOT,read_json,atomic_json
class Probe(ContactEngine):
 def motor_gate(self,net,amp,theta):return np.full(6,self.fixed) if self.fixed is not None else super().motor_gate(net,amp,theta)
def run(case):
 name,gate,learned=case;e=Probe();e.fixed=gate;n,d=Engine().synthetic(82001,count=100)
 t=np.r_[read_json(ROOT/'checkpoints/v4b_primary.json')['parameters'],np.zeros(6)] if learned else INITIAL.copy();start=time.monotonic();r=e.rollout(t,n,d)
 return dict(name=name,metric=brief(r['metrics'][2]),wall_s=time.monotonic()-start,warnings=r['solver_warnings'],actual=r['actual'],notes=n)
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(4) as pool:rr=list(pool.map(run,[('contact_legacy',None,True),('contact_full_seed',1,True),('contact_full_neutral',1,False),('contact_threequarter',.75,False)]))
 atomic_json(ROOT/'research/contact_probe.json',dict(seed=82001,count=100,targets='Exact same targets as decoder_probe; calibration only',results=rr));print(json.dumps([{k:v for k,v in r.items() if k not in ['actual','notes']} for r in rr]))
