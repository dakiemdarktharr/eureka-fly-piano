from pathlib import Path
import os,sys,json,tempfile
FROZEN=bool(getattr(sys,'frozen',False))
PROJECT=Path(sys._MEIPASS)/'bundle/project' if FROZEN else Path(__file__).resolve().parent.parent
ROOT=PROJECT/'v5'
V2=PROJECT/'v2';V3=PROJECT/'v3'
STATE=Path(os.environ.get('FLYPIANO_V5_STATE',str((Path(sys.executable).parent if FROZEN else ROOT)/'runtime'))).resolve()
for p in [PROJECT,V2]:
 if str(p) not in sys.path:sys.path.insert(0,str(p))
def read_json(p):return json.loads(Path(p).read_text(encoding='utf8'))
def atomic_json(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);fd,n=tempfile.mkstemp(dir=p.parent,suffix='.tmp')
 try:
  with os.fdopen(fd,'w',encoding='utf8') as f:json.dump(obj,f,ensure_ascii=False,allow_nan=False,indent=2)
  os.replace(n,p)
 finally:
  if os.path.exists(n):os.unlink(n)
