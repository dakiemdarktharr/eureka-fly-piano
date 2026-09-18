"""Private standalone Windows app. Licensed assets and user scores stay local."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
args=[sys.executable,'-m','PyInstaller','--noconfirm','--onedir','--windowed','--name','FlyPianoLabV4','--distpath',str(ROOT/'dist'),'--workpath',str(ROOT/'build'),'--specpath',str(ROOT/'build'),'--paths',str(ROOT),'--paths',str(PROJECT/'v2'),'--paths',str(PROJECT),'--collect-all','mujoco','--hidden-import','scipy.optimize','--hidden-import','psutil','--collect-submodules','scipy._external.array_api_compat','--collect-submodules','scipy._external.array_api_extra']
for package in ['flygym','music21','matplotlib','IPython','pyarrow','trimesh','pytest','torch','warp','mujoco_warp']:args+=['--exclude-module',package]
def add(src,dest):args.extend(['--add-data',f'{src}:{dest}'])
add(ROOT/'ui','bundle/project/v4/ui')
add(ROOT/'checkpoints','bundle/project/v4/checkpoints')
for name in ['engine.py','train.py','train_songs.py','v4_paths.py']:add(ROOT/name,'bundle/project/v4')
add(PROJECT/'v2/world.py','bundle/project/v2')
add(PROJECT/'simulation/model.py','bundle/project/simulation')
for p in ['output','research']:
 if p=='output' and (ROOT/p).exists():add(ROOT/p,'bundle/project/v4/'+p)
if (ROOT/'research/cpu_benchmark.json').exists():add(ROOT/'research/cpu_benchmark.json','bundle/project/v4/research')
add(PROJECT/'v2/ui/vendor','bundle/project/v2/ui/vendor')
for name in ['scene.json','brain.json','attribution.json','fly_model','licenses']:
 p=PROJECT/'v2/assets'/name;add(p,'bundle/project/v2/assets/'+name if p.is_dir() else 'bundle/project/v2/assets')
for key in ['merry','pool']:
 for suffix in ['score.json','reference.mid']:add(PROJECT/f'v2/data/{key}_{suffix}','bundle/project/v2/data')
add(PROJECT/'v2/data/ik_cache.npz','bundle/project/v2/data')
for name in ['weights.npy','neurons.csv']:add(PROJECT/'connectome'/name,'bundle/project/connectome')
add(PROJECT/'connectome_manifest.json','bundle/project')
for p in (PROJECT/'v2/scores/private').glob('*.pdf'):add(p,'bundle/project/v2/scores/private')
args.append(str(ROOT/'app.py'));subprocess.run(args,check=True)
print(ROOT/'dist/FlyPianoLabV4/FlyPianoLabV4.exe')
