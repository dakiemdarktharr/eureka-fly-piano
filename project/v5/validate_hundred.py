"""Reproducible 100-target diagnostic and cue sensitivity; not model selection."""
import json,time,hashlib
from pathlib import Path
import numpy as np
from engine import Engine,INITIAL,LOW,HIGH
from train_hundred import clip
from v4_paths import ROOT,STATE,atomic_json,read_json

def main():
 e=Engine();notes,d=e.synthetic(91001,count=100)
 assert len(notes)==100 and len({n['id'] for n in notes})==100
 assert len(INITIAL)==len(LOW)==len(HIGH)==55
 anatomy=read_json(ROOT/'assets/manc.json')
 assert [n['id'] for n in anatomy['neurons']]==e.template.table.bodyId.astype(str).tolist()
 assert not anatomy['missing']
 coverage={}
 for key in ['merry','pool']:
  song,_=e.song(key);seen=set()
  for i in sorted(set(list(range(0,len(song)-99,100))+[len(song)-100])):
   block,_=clip(song,i);assert len(block)==100;seen.update(n['id'] for n in block)
  assert len(seen)==len(song);coverage[key]=len(seen)
 source=read_json(ROOT/'checkpoints/v4b_primary.json');theta=np.r_[source['parameters'],np.zeros(6)]
 out=STATE/'preview';out.mkdir(parents=True,exist_ok=True);start=time.monotonic()
 r,frames=e.rollout(theta,notes,d,record=True)
 assert r['metrics'][2]['target_notes']==100 and not r['solver_warnings']
 assert frames.shape==(r['frame_count'],r['stride']) and np.isfinite(frames).all()
 off=r['layout']['neuron_rates'][0];assert r['stride']-off==412
 assert np.array_equal(frames[:,r['layout']['DN'][0]:r['layout']['DN'][0]+2],frames[:,off+e.template.dn])
 r.update(piece='skill',preview=False,diagnostic=True,evaluation_scope='100 synthetic targets; existing v4b checkpoint + zero new cue gains; no parameter selection from this evaluation')
 frames.tofile(out/'skill.bin');r['replay_sha256']=hashlib.sha256((out/'skill.bin').read_bytes()).hexdigest();atomic_json(out/'skill.json',r)
 variants={'cue_zero':r['metrics'][2]}
 for gain in [10.,30.]:
  t=theta.copy();t[49:]=gain;v=e.rollout(t,notes,d);assert v['metrics'][2]['target_notes']==100
  variants[f'fixed_cue_{int(gain)}']=dict(v['metrics'][2],solver_warnings=v['solver_warnings'])
  print('cue',gain,variants[f'fixed_cue_{int(gain)}'],flush=True)
 report=dict(target_count=100,physics_duration_s=d,coverage=coverage,neurons=412,trace_matches_dn=True,finite_frames=True,variants=variants,wall_s=time.monotonic()-start,scope='Single seed cue sensitivity; not causal proof, generalization claim, or optimization. Fixed-gain variants never select the warm start.')
 atomic_json(ROOT/'results/hundred_validation.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
