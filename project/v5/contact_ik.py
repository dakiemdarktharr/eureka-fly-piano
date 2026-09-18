"""Calibrate the existing mesh contact surface; do not change physical geometry."""
import hashlib,json,time
from pathlib import Path
import numpy as np
import mujoco as mj
from engine import Engine
from v4_paths import ROOT,atomic_json

def support_point(world,data,geom):
 m=world.model;mesh=m.geom_dataid[geom];start=m.mesh_vertadr[mesh];count=m.mesh_vertnum[mesh]
 vertices=m.mesh_vert[start:start+count]@data.geom_xmat[geom].reshape(3,3).T+data.geom_xpos[geom]
 return vertices[np.argmin(vertices[:,2])].copy()

def inverse(world,leg,target,start):
 m=world.model;d=world.ikdata;ids=world.qids[leg];dofs=world.dofs[leg];geom=list(world.toe_geoms)[leg]
 d.qpos[:]=world.neutral_q;d.qpos[ids]=start
 for _ in range(90):
  mj.mj_forward(m,d);point=support_point(world,d,geom);error=target-point
  if np.linalg.norm(error)<.003:break
  mj.mj_jac(m,d,world.jac,world.jacr,point,int(world.toes[leg]));j=world.jac[:,dofs]
  delta=j.T@np.linalg.solve(j@j.T+np.eye(3)*.003,error)
  d.qpos[ids]=np.clip(d.qpos[ids]+np.clip(delta,-.08,.08),world.neutral_q[ids]-1.35,world.neutral_q[ids]+1.35)
 mj.mj_forward(m,d)
 return d.qpos[ids].copy(),float(np.linalg.norm(target-support_point(world,d,geom)))

def prepare():
 e=Engine();w=e.w;hover=e.hover.copy();press=e.press.copy();errors=e.errors.copy();start=time.monotonic()
 for leg in range(6):
  for pitch in range(21,109):
   hover[leg,pitch-21],_=inverse(w,leg,w.target(leg,pitch,.14),e.hover[leg,pitch-21])
   press[leg,pitch-21],errors[leg,pitch-21]=inverse(w,leg,w.target(leg,pitch,-.15),e.press[leg,pitch-21])
  print('Contact IK leg',leg,'done',flush=True)
 out=ROOT/'assets/ik_contact_v5.npz';np.savez(out,hover=hover,press=press,error=errors)
 atomic_json(ROOT/'research/contact_ik.json',dict(method='Jacobian IK at lowest mesh vertex; original contact mesh, servo limits and physics unchanged',iterations=90,tolerance_mm=.003,wall_s=time.monotonic()-start,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),median_error_mm=float(np.median(errors)),max_error_mm=float(errors.max())))

class ContactEngine(Engine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);c=np.load(ROOT/'assets/ik_contact_v5.npz');self.hover=c['hover'];self.press=c['press'];self.errors=c['error']
  for leg in range(6):
   pitch=int(np.clip(round(self.w.neutral_feet[leg,1]/.055+64),21,108));self.idle[self.w.acts[leg]]=self.hover[leg,pitch-21]
  self.pitches=[np.argsort(self.errors[leg])[:12]+21 for leg in range(6)]

if __name__=='__main__':prepare()
