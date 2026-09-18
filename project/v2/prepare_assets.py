from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parent
mesh=trimesh.load(ROOT/'assets/raw/FLYWIRE.ply')
vertices=np.asarray(mesh.vertices)/1000
center=(vertices.min(0)+vertices.max(0))/2
brain={'vertices':(vertices-center).round(3).tolist(),'faces':mesh.faces.tolist(),'coordinate_system':'FlyWire physical nm converted to µm; shared centering only','center_um':center.tolist(),'scope':'Two type/side-matched DNg100 homologs. Modeled VNC DN activity projected across specimens; no recorded brain activity.','neurons':[]}
for side,rid,manc in [('left','720575940640978048','10093'),('right','720575940647228468','10339')]:
 p=ROOT/f'assets/raw/{rid}.json';s=json.loads(p.read_text())
 brain['neurons'].append({'id':rid,'manc_id':manc,'side':side,'type':'DNg100','vertices':(np.array(s['vertices_um'])-center).round(3).tolist(),'edges':s['edges'],'source':s['source'],'sha256':s['sha256']})
(ROOT/'assets/brain.json').write_text(json.dumps(brain,separators=(',',':')),encoding='utf8')
print('Brain:',len(vertices),'mesh vertices; neurons:',[(n['side'],len(n['vertices'])) for n in brain['neurons']])
