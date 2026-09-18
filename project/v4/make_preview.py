"""Untrained synthetic preflight, explicitly outside the learning campaign."""
from engine import Engine,INITIAL
from v4_paths import STATE,atomic_json
e=Engine();notes,d=e.synthetic(80001,count=6);r,f=e.rollout(INITIAL,notes,d,record=True)
r.update(preview=True,diagnostic=True,controller='Untrained v4 preflight; seed 80001; not held-out test')
out=STATE/'preview';out.mkdir(parents=True,exist_ok=True);f.tofile(out/'skill.bin');atomic_json(out/'skill.json',r)
print(out)
