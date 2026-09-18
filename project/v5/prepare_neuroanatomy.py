"""Download real MANC morphology; deterministic display decimation, no fake paths."""
import concurrent.futures, csv, hashlib, io, json, urllib.request
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
BASE='https://storage.googleapis.com/lee-lab_brain-and-nerve-cord-fly-connectome/compiled_data/manc_121/'
RAW=ROOT/'assets/raw';RAW.mkdir(parents=True,exist_ok=True)

def download(relative):
    p=RAW/Path(relative).name
    if not p.exists():
        with urllib.request.urlopen(BASE+relative,timeout=90) as response: data=response.read()
        p.write_bytes(data)
    return p

def neuron(row):
    id=row['bodyId'];p=download(f'manc_manc_space_swc/{id}.swc')
    a=np.loadtxt(io.StringIO(p.read_text()),comments='#');ids={int(x):i for i,x in enumerate(a[:,0])}
    # Native MANC SWCs and the explicitly micron mesh agree in micrometers.
    # Two DN exports have incompatible coordinates; exclude rather than invent a transform.
    coordinate_valid=bool(np.max(np.abs(a[:,2:5]))<2000)
    points=a[:,2:5];edges=np.array([(i,ids[int(x)]) for i,x in enumerate(a[:,6]) if int(x) in ids],int)
    # Retain sampled real segments, never join unrelated points into invented branches.
    take=np.linspace(0,len(edges)-1,min(len(edges),600)).astype(int);segments=points[edges[take]].reshape(-1,3)
    return dict(id=id,type=row['type'],instance=row['instance'],kind=row['kind'],leg=int(row['leg']),
                region=row['region'],side=row['somaSide'] or row['rootSide'],
                segments=segments.round(3).tolist() if coordinate_valid else [],coordinate_valid=coordinate_valid,coordinate_note='Native micron coordinates' if coordinate_valid else 'Excluded: source SWC coordinate scale/space disagrees with native MANC mesh; no inferred transform',source=BASE+f'manc_manc_space_swc/{id}.swc',
                sha256=hashlib.sha256(p.read_bytes()).hexdigest(),original_edges=len(edges),shown_edges=len(take))

def main():
    rows=list(csv.DictReader((PROJECT/'connectome/neurons.csv').open(encoding='utf8')))
    neurons=[];errors=[]
    with concurrent.futures.ThreadPoolExecutor(6) as pool:
        futures={pool.submit(neuron,r):r for r in rows}
        for f in concurrent.futures.as_completed(futures):
            try:neurons.append(f.result())
            except Exception as ex:errors.append(dict(id=futures[f]['bodyId'],error=str(ex)))
            if (len(neurons)+len(errors))%50==0:print(len(neurons),'morphologies;',len(errors),'errors',flush=True)
    idx={r['bodyId']:i for i,r in enumerate(rows)};neurons.sort(key=lambda n:idx[n['id']])
    p=download('obj/manc_neuropil_microns.obj');vertices=[];faces=[]
    for line in p.read_text().splitlines():
        parts=line.split()
        if parts and parts[0]=='v':vertices.append([float(x) for x in parts[1:4]])
        if parts and parts[0]=='f':
            v=[int(x.split('/')[0])-1 for x in parts[1:]]
            for j in range(1,len(v)-1):faces.append([v[0],v[j],v[j+1]])
    center=(np.min(vertices,axis=0)+np.max(vertices,axis=0))/2
    vertices=(np.array(vertices)-center).round(3).tolist()
    for n in neurons:
        if n['segments']: n['segments']=(np.array(n['segments'])-center).round(3).tolist()
        n['index']=idx[n['id']]
    output=dict(dataset='MANC v1.2.1 morphology',coordinate_system='MANC native micrometers, shared center; incompatible source coordinates excluded',center_um=center.tolist(),neurons=neurons,vertices=vertices,faces=faces,missing=errors,
                scope='Morphology matched by MANC bodyId. Graph export release not recorded; same-ID correspondence is not independent cell-type validation.',
                source=BASE,license='MANC CC-BY; see https://www.janelia.org/project-team/flyem/manc-connectome',
                mesh_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (ROOT/'assets/manc.json').write_text(json.dumps(output,separators=(',',':')),encoding='utf8')
    print('Finished',len(neurons),'/',len(rows),'neurons; missing',len(errors),flush=True)

if __name__=='__main__':main()
