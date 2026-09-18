"""Tethered NeuroMechFly 2.1.0 with physical miniature keyboard.

Native fly units: mm, g, s. Keyboard and controller parameters are engineering
assumptions, not measured piano or fly-muscle properties. No kinematic teleport
is used during dynamic execution; IK is only an explicit low-level goal decoder.
"""
from pathlib import Path
import json
import numpy as np
import mujoco as mj

ROOT=Path(__file__).resolve().parent
LEGS=['lf','rf','lm','rm','lh','rh']
KEY_MIN,KEY_MAX=21,108
KEY_SPACING=.055
KEY_Z=-.12

def build_model(dt=.0002):
    source=ROOT/'assets/fly_model/piano_fly.xml'
    if not source.exists():
        from flygym.compose import NeuroMechFly,KinematicPosePreset
        from flygym.anatomy import AxisOrder,JointPreset,Skeleton,ActuatedDOFPreset
        fly=NeuroMechFly(name='piano_fly')
        skeleton=Skeleton(joint_preset=JointPreset.ALL_BIOLOGICAL,axis_order=AxisOrder.ROLL_PITCH_YAW)
        fly.add_joints(skeleton,neutral_pose=KinematicPosePreset.NEUTRAL)
        fly.add_actuators(skeleton.get_actuated_dofs_from_preset(ActuatedDOFPreset.LEGS_ACTIVE_ONLY),actuator_type='position',neutral_input=KinematicPosePreset.NEUTRAL,kp=50)
        fly.colorize();fly.save_xml_with_assets(str(source.parent))
    spec=mj.MjSpec.from_file(str(source))
    spec.option.timestep=dt
    spec.option.integrator=mj.mjtIntegrator.mjINT_IMPLICITFAST
    spec.option.iterations=50
    for geom in spec.worldbody.find_all('geom'):
        if geom.name.endswith('tarsus5'):
            geom.contype=1;geom.conaffinity=2;geom.friction=[.6,.005,.0001]
    for pitch in range(KEY_MIN,KEY_MAX+1):
        y=(pitch-64)*KEY_SPACING
        black=pitch%12 in [1,3,6,8,10]
        body=spec.worldbody.add_body(name=f'key_{pitch}',pos=[0,y,KEY_Z-.025])
        body.add_joint(name=f'key_slide_{pitch}',type=mj.mjtJoint.mjJNT_SLIDE,axis=[0,0,1],limited=True,range=[-.045,0],stiffness=[5],damping=[.006])
        body.add_geom(name=f'key_geom_{pitch}',type=mj.mjtGeom.mjGEOM_BOX,size=[2.25,KEY_SPACING*.45,.025],mass=.000002,rgba=[.08,.12,.17,1] if black else [.8,.86,.88,1],contype=2,conaffinity=1,friction=[.6,.005,.0001])
    # Keys are compliant; the thorax remains fixed in the source model.
    model=spec.compile();data=mj.MjData(model)
    if model.nkey:mj.mj_resetDataKeyframe(model,data,0)
    mj.mj_forward(model,data)
    return model,data

class PianoWorld:
    def __init__(self,dt=.0002):
        self.model,self.data=build_model(dt);m=self.model;d=self.data
        self.neutral_ctrl=d.ctrl.copy();self.neutral_q=d.qpos.copy()
        self.toes=np.array([mj.mj_name2id(m,mj.mjtObj.mjOBJ_BODY,l+'_tarsus5') for l in LEGS])
        self.neutral_feet=d.xpos[self.toes].copy()
        self.acts=[];self.qids=[];self.dofs=[]
        for leg in LEGS:
            aa=[i for i in range(m.nu) if ('-'+leg+'_') in mj.mj_id2name(m,mj.mjtObj.mjOBJ_ACTUATOR,i)]
            self.acts.append(np.array(aa));j=m.actuator_trnid[aa,0]
            self.qids.append(m.jnt_qposadr[j]);self.dofs.append(m.jnt_dofadr[j])
        self.key_geoms={mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,f'key_geom_{p}'):p for p in range(KEY_MIN,KEY_MAX+1)}
        self.key_qids=np.array([m.jnt_qposadr[mj.mj_name2id(m,mj.mjtObj.mjOBJ_JOINT,f'key_slide_{p}')] for p in range(KEY_MIN,KEY_MAX+1)])
        self.toe_geoms={mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,l+'_tarsus5'):i for i,l in enumerate(LEGS)}
        self.ikdata=mj.MjData(m);self.ikdata.qpos[:]=self.neutral_q
        self.jac=np.zeros((3,m.nv));self.jacr=np.zeros((3,m.nv));self.forcebuf=np.zeros(6)

    def target(self,leg,pitch,z=KEY_Z+.11):
        return np.array([self.neutral_feet[leg,0],(pitch-64)*KEY_SPACING,z])

    def inverse(self,leg,target,start=None,iterations=60):
        m=self.model;d=self.ikdata;ids=self.qids[leg];dofs=self.dofs[leg]
        d.qpos[:]=self.neutral_q
        if start is not None:d.qpos[ids]=start
        for _ in range(iterations):
            mj.mj_forward(m,d);error=target-d.xpos[self.toes[leg]]
            if np.linalg.norm(error)<.006:break
            mj.mj_jacBody(m,d,self.jac,self.jacr,int(self.toes[leg]));j=self.jac[:,dofs]
            delta=j.T@np.linalg.solve(j@j.T+np.eye(3)*.003,error)
            d.qpos[ids]+=np.clip(delta,-.10,.10)
            # Explicit engineering displacement limits around the source neutral pose.
            d.qpos[ids]=np.clip(d.qpos[ids],self.neutral_q[ids]-1.35,self.neutral_q[ids]+1.35)
        mj.mj_forward(m,d)
        return d.qpos[ids].copy(),float(np.linalg.norm(target-d.xpos[self.toes[leg]]))

    def step(self,ctrl,external=None):
        d=self.data;m=self.model;d.ctrl[:]=ctrl;d.xfrc_applied[:]=0
        if external is not None:d.xfrc_applied[self.toes[external[0]],:3]=external[1]
        mj.mj_step(m,d)
        if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():raise FloatingPointError('Physics diverged')

    def contacts(self):
        result={}
        for i in range(self.data.ncon):
            c=self.data.contact[i];a,b=int(c.geom1),int(c.geom2)
            if a in self.key_geoms and b in self.toe_geoms:p,leg=self.key_geoms[a],self.toe_geoms[b]
            elif b in self.key_geoms and a in self.toe_geoms:p,leg=self.key_geoms[b],self.toe_geoms[a]
            else:continue
            mj.mj_contactForce(self.model,self.data,i,self.forcebuf)
            result[(p,leg)]=result.get((p,leg),0)+max(0,float(self.forcebuf[0]))
        return result

    def scene(self):
        m=self.model;d=self.data;geoms=[]
        for g in range(m.ngeom):
            if m.geom_type[g]!=mj.mjtGeom.mjGEOM_MESH:continue
            mesh=m.geom_dataid[g];vs=m.mesh_vertadr[mesh];fs=m.mesh_faceadr[mesh]
            geoms.append({'geom_id':g,'name':mj.mj_id2name(m,mj.mjtObj.mjOBJ_GEOM,g),'vertices':m.mesh_vert[vs:vs+m.mesh_vertnum[mesh]].round(6).tolist(),'faces':m.mesh_face[fs:fs+m.mesh_facenum[mesh]].tolist(),'color':m.geom_rgba[g].tolist()})
        return {'geoms':geoms,'key_min':KEY_MIN,'key_max':KEY_MAX,'key_spacing':KEY_SPACING,'key_z':KEY_Z,'body_model':'NeuroMechFly/FlyGym 2.1.0; fixed thorax, custom miniature keyboard','physics':'MuJoCo 3.9.0; mm,g,s; position servos are engineered'}

    def pose(self):
        ids=[g for g in range(self.model.ngeom) if self.model.geom_type[g]==mj.mjtGeom.mjGEOM_MESH]
        # World positions and rotation matrices, directly from the dynamic state.
        return np.concatenate([self.data.geom_xpos[ids],self.data.geom_xmat[ids]],axis=1).astype(np.float32)

if __name__=='__main__':
    w=PianoWorld();print('Physics',w.model.nq,w.model.nu,w.model.nbody)
    q,e=w.inverse(0,w.target(0,80));print('IK',e,q)
    ctrl=w.neutral_ctrl.copy();ctrl[w.acts[0]]=q
    for _ in range(5000):w.step(ctrl)
    print('Final toe',w.data.xpos[w.toes[0]],'contacts',w.contacts())
    (ROOT/'assets/scene.json').write_text(json.dumps(w.scene(),separators=(',',':')))
