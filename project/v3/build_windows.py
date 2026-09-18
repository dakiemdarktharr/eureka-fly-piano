"""Create a private standalone Windows folder bundle; never upload its data."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
args=[sys.executable,'-m','PyInstaller','--noconfirm','--onedir','--windowed','--name','FlyPianoLab','--distpath',str(ROOT/'dist'),'--workpath',str(ROOT/'build'),'--specpath',str(ROOT/'build'),'--paths',str(ROOT),'--paths',str(PROJECT/'v2'),'--paths',str(PROJECT),'--collect-all','mujoco','--hidden-import','scipy.optimize','--hidden-import','psutil','--collect-submodules','scipy._external.array_api_compat','--collect-submodules','scipy._external.array_api_extra']
for package in ['flygym','music21','matplotlib','IPython','pyarrow','trimesh','pytest']:args+=['--exclude-module',package]
def add(source,dest):args.extend(['--add-data',f'{source}:{dest}'])
add(ROOT/'ui','bundle/project/v3/ui')
if (ROOT/'output').exists():add(ROOT/'output','bundle/project/v3/output')
add(PROJECT/'v2/ui/vendor','bundle/project/v2/ui/vendor')
for p in ['scene.json','brain.json','attribution.json','fly_model','licenses']:add(PROJECT/'v2/assets'/p,'bundle/project/v2/assets/'+p if (PROJECT/'v2/assets'/p).is_dir() else 'bundle/project/v2/assets')
for key in ['merry','pool']:
 for suffix in ['score.json','full.json','full.bin','constant.json','constant.bin','reference.mid']:
  source=PROJECT/'v2/data'/f'{key}_{suffix}'
  if source.exists():add(source,'bundle/project/v2/data')
add(PROJECT/'v2/data/ik_cache.npz','bundle/project/v2/data')
for p in ['weights.npy','neurons.csv']:add(PROJECT/'connectome'/p,'bundle/project/connectome')
add(PROJECT/'connectome_manifest.json','bundle/project')
for p in (PROJECT/'v2/scores/private').glob('*.pdf'):add(p,'bundle/project/v2/scores/private')
args.append(str(ROOT/'app.py'))
subprocess.run(args,check=True)
print(ROOT/'dist/FlyPianoLab/FlyPianoLab.exe')
