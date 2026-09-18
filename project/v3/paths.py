from pathlib import Path
import os,sys,json,tempfile

FROZEN=getattr(sys,'frozen',False)
PROJECT=Path(sys._MEIPASS)/'bundle/project' if FROZEN else Path(__file__).resolve().parents[1]
V2=PROJECT/'v2';V3=PROJECT/'v3'
STATE=Path(os.environ.get('FLYPIANO_STATE',str((Path(sys.executable).parent/'runtime') if FROZEN else V3/'runtime'))).resolve()
RUNS=STATE/'runs'
for p in (PROJECT,V2):
 if str(p) not in sys.path:sys.path.insert(0,str(p))

def read_json(path):return json.loads(Path(path).read_text(encoding='utf8'))
def atomic_json(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 fd,name=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
 try:
  with os.fdopen(fd,'w',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,allow_nan=False,indent=2)
  os.replace(name,path)
 finally:
  if os.path.exists(name):os.unlink(name)

def readiness():
 required=[V2/'data/ik_cache.npz',V2/'assets/fly_model/piano_fly.xml',V2/'assets/brain.json',V2/'assets/scene.json',V2/'data/merry_score.json',V2/'data/pool_score.json',PROJECT/'connectome/weights.npy',PROJECT/'connectome/neurons.csv',PROJECT/'connectome_manifest.json']
 missing=[str(p.relative_to(PROJECT)) for p in required if not p.is_file()]
 return {'ready':not missing,'missing':missing,'version':'3.0.0','state_dir':str(STATE),'score_accuracy':'provisional OMR; no independent note-level verification'}
