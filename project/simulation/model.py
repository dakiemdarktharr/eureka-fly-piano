"""Measured rate network + explicitly engineered task relay, feedback and decoder."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

ROOT=Path(__file__).resolve().parents[1]
class MotorNetwork:
    def __init__(self,seed=0,variant='full',dt=.001):
        self.table=pd.read_csv(ROOT/'connectome/neurons.csv',keep_default_na=False)
        self.manifest=json.loads((ROOT/'connectome_manifest.json').read_text())
        w=np.load(ROOT/'connectome/weights.npy');self.variant=variant;self.dt=dt
        self.rng=np.random.default_rng(seed);n=len(w);self.r=np.zeros(n);self.task=np.zeros(8)
        self.dn=np.flatnonzero(self.table.kind=='DN');self.cpg=np.flatnonzero(self.table.kind=='CPG')
        self.mn=[np.flatnonzero((self.table.kind=='MN') & (self.table.leg==i)) for i in range(6)]
        self.e1=[np.flatnonzero((self.table.type=='IN17A001') & (self.table.leg==i))[0] for i in range(6)]
        s=self.table['size'].to_numpy(float)/self.manifest['normalization_median_volume']
        self.a=np.maximum(.01,self.rng.normal(1,.1,n))/s
        self.th=np.maximum(.01,self.rng.normal(7.5,.6,n))*s
        self.cap=np.maximum(1,self.rng.normal(200,10,n))
        self.tau=np.maximum(.005,self.rng.normal(.02,.002,n))
        self.swap_count=0
        if variant=='randomized':w,self.swap_count=rewire(w,self.rng)
        if variant=='no_cpg': w[self.cpg,:]=0;w[:,self.cpg]=0
        if variant=='no_dn':w[self.dn,:]=0
        if variant=='no_inhibition':w[w<0]=0
        legs=self.table.leg.to_numpy()
        if variant=='no_interleg':w[(legs[:,None]!=legs[None,:])&(legs[:,None]>=0)&(legs[None,:]>=0)]=0
        if variant=='no_intraleg':w[(legs[:,None]==legs[None,:])&(legs[:,None]>=0)&(legs[None,:]>=0)]=0
        self.w=csr_matrix(w.T*.03)
        self.delay=0 if variant=='no_delay' else max(1,round(.004/dt))
        self.history=[np.zeros(n) for _ in range(self.delay+1)];self.step_count=0
        if variant=='rnn':
            # Fixed random rate reservoir, state-size-matched, untrained control.
            rw=self.rng.normal(0,1/np.sqrt(n),(n,n));self.rw=rw*.8
    def step(self,drive,key,feedback=None,cue=True):
        target=np.zeros(8)
        if key>=0 and cue:target[key]=1
        self.task+=self.dt/.025*(target-self.task)
        inp=np.zeros(len(self.r));inp[self.dn]=drive
        if self.variant=='no_dn':inp[self.dn]=0
        if feedback is not None and self.variant!='no_feedback':
            inp[self.e1]+=np.clip(feedback,-1,1)*10 # assumed sensory projection
        delayed=self.history[self.step_count%len(self.history)] if self.delay else self.r
        if self.variant=='rnn':
            desired=100*np.maximum(0,np.tanh(self.rw@(delayed/100)+inp/200))
        else:
            desired=np.maximum(0,self.cap*np.tanh(self.a/self.cap*(inp+self.w@delayed-self.th)))
        self.r+=self.dt/self.tau*(desired-self.r)
        if self.variant=='no_cpg':self.r[self.cpg]=0
        if self.variant=='no_dn':self.r[self.dn]=0
        self.history[self.step_count%len(self.history)]=self.r.copy();self.step_count+=1
        if not np.isfinite(self.r).all():raise FloatingPointError('neural divergence')
        # Fixed population sum, globally scaled; no per-frame normalization.
        return np.array([self.r[m].sum()/40 if len(m) else 0 for m in self.mn])

def rewire(w,rng,attempts_factor=30):
    """Directed double-edge swap: preserve in/out degree and source NT sign.
    Outgoing weights remain attached to their sources. Not strength-preserving.
    Self-edges and duplicates are rejected; existing self-edges left untouched.
    """
    out=w.copy();edges=np.argwhere(w!=0);count=0
    for _ in range(len(edges)*attempts_factor):
        i,j=rng.integers(0,len(edges),2);a,b=edges[i];c,d=edges[j]
        if a==c or b==d or a==d or c==b or a==b or c==d:continue
        if out[a,d]!=0 or out[c,b]!=0:continue
        out[a,d],out[c,b]=out[a,b],out[c,d];out[a,b]=out[c,d]=0
        edges[i,1]=d;edges[j,1]=b;count+=1
    assert np.array_equal((out!=0).sum(0),(w!=0).sum(0))
    assert np.array_equal((out!=0).sum(1),(w!=0).sum(1))
    return out,count


