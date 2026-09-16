"""Six independent 2R legs, damped torque dynamics and unilateral key contact.
Units are nondimensional. Torques/forces must NOT be read as measured fly units.
The body is tethered; no whole-body locomotion, adhesion or musculoskeletal claim.
"""
import numpy as np

LEGS=['LF','RF','LM','RM','LH','RH']
class Body:
    def __init__(self,nkeys=8,layout='standard',disabled=-1):
        self.nkeys=nkeys; self.disabled=disabled
        self.x=np.linspace(-.65,.65,nkeys)
        if layout=='mirrored': self.x=self.x[::-1].copy()
        if layout=='shifted': self.x+=.12
        if layout=='spacing': self.x*=1.15
        self.height=-.85 if layout!='height' else -.76
        self.hips=np.array([[-.22,0],[.22,0],[-.22,-.06],[.22,-.06],[-.22,-.12],[.22,-.12]])
        self.q=np.array([self.ik(i, self.hips[i,0],-.62) for i in range(6)])
        self.dq=np.zeros((6,2)); self.tau=np.zeros((6,2)); self.force=np.zeros(6)
        self.actual=np.full(6,-1); self.last_contact=np.zeros(6,bool)
    def ik(self,leg,x,z):
        u=x-self.hips[leg,0]; v=z-self.hips[leg,1]; l=.65
        c=np.clip((u*u+v*v-2*l*l)/(2*l*l),-.999,.999)
        b=np.arccos(c); a=np.arctan2(v,u)-np.arctan2(l*np.sin(b),l+l*np.cos(b))
        return np.array([a,b])
    def points(self):
        a=self.q[:,0]; b=self.q.sum(1)
        knee=self.hips+.65*np.stack([np.cos(a),np.sin(a)],1)
        foot=knee+.65*np.stack([np.cos(b),np.sin(b)],1)
        return knee,foot
    def step(self,targets,dt,kp=32,kd=1.4):
        self.tau=np.clip(kp*(targets-self.q)-kd*self.dq,-8,8)
        if self.disabled>=0:self.tau[self.disabled]=0;self.dq[self.disabled]=0
        knee,foot=self.points(); ext=np.zeros((6,2)); self.force[:]=0; self.actual[:]=-1
        for i in range(6):
            if i==self.disabled: continue
            key=int(np.argmin(abs(self.x-foot[i,0])))
            width=abs(self.x[1]-self.x[0])*.44 if self.nkeys>1 else .1
            if abs(self.x[key]-foot[i,0])<width and foot[i,1]<self.height:
                a,b=self.q[i,0],self.q[i].sum()
                jz=np.array([.65*np.cos(a)+.65*np.cos(b),.65*np.cos(b)])
                vz=float(jz@self.dq[i]); force=max(0,180*(self.height-foot[i,1])-1.5*vz)
                self.force[i]=force; self.actual[i]=key;ext[i]=jz*force
        self.dq+=dt*(self.tau+ext-.25*self.dq)/.08
        self.q+=dt*self.dq
        if not np.isfinite(self.q).all():raise FloatingPointError('body diverged')
        on=self.force>.04; rising=on & ~self.last_contact;self.last_contact=on
        return rising
