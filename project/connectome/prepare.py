"""Fetch pinned public artifacts; extract a measured motor graph without inventing edges."""
from pathlib import Path
import json, hashlib, urllib.request, zipfile, warnings
import numpy as np
import pandas as pd
import rdata

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = '10e7661bf414ba7b4c2edf795cd36d0f878c17c0'
ANATOMY = 'd24c79554a58f7cf985e71d2578ad86423667413'
FILES = {
 'W_20260522_allSynapses.npz': f'https://raw.githubusercontent.com/smpuglie/Pugliese_cpg_2025/{UPSTREAM}/data/manc%20full%20vnc%20data/W_20260522_allSynapses.npz',
 'wTable_20260522_allSynapses.feather': f'https://raw.githubusercontent.com/smpuglie/Pugliese_cpg_2025/{UPSTREAM}/data/manc%20full%20vnc%20data/wTable_20260522_allSynapses.feather',
 'MANC.tissue.surf.rda': f'https://raw.githubusercontent.com/natverse/malevnc/{ANATOMY}/data/MANC.tissue.surf.rda',
 'MANC.surf.rda': f'https://raw.githubusercontent.com/natverse/malevnc/{ANATOMY}/data/MANC.surf.rda',
}
EXPECTED_SHA256 = {'W_20260522_allSynapses.npz': '3cd637b2397236aec4c8d46883b753335f73e3acae508f9c082f39bd123e0b84', 'wTable_20260522_allSynapses.feather': 'a013ec9910d5377bf8b90b9abdd6411bf29f934141228be3d677962a047b7522', 'MANC.tissue.surf.rda': 'b294410076f75e4ac389030a15732f562eae46f366330d2062b39cdab3211655', 'MANC.surf.rda': '37b594f248d18bf478d66d9e0b572beedd9e98c39a502735d0636cb6f974ba17'}

def sha(path):
    with open(path,'rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False), encoding='utf8')

def prepare():
    raw=ROOT/'data/external'; raw.mkdir(parents=True,exist_ok=True)
    for name,url in FILES.items():
        if not (raw/name).exists(): urllib.request.urlretrieve(url, raw/name)
        if sha(raw/name) != EXPECTED_SHA256[name]:
            raise ValueError(f'Source checksum mismatch: {name}; refusing to build a different graph')
    df=pd.read_feather(raw/'wTable_20260522_allSynapses.feather')
    keep=df.type.isin(['DNg100','IN17A001','INXXX466','IN16B036']) | ((df['class']=='motor neuron') & df.subclass.isin(['fl','ml','hl']))
    ix=np.flatnonzero(keep); table=df.iloc[ix].copy().reset_index(drop=True)
    # The compressed upstream file stores a dense pre-by-post matrix. Stream it
    # by its declared memory order to avoid allocating the full 4.47 GB matrix.
    selected={int(old):new for new,old in enumerate(ix)}
    w=np.zeros((len(ix),len(ix)))
    with zipfile.ZipFile(raw/'W_20260522_allSynapses.npz') as z, z.open('arr_0.npy') as f:
        version=np.lib.format.read_magic(f)
        shape,fortran,dtype=(np.lib.format.read_array_header_1_0 if version==(1,0) else np.lib.format.read_array_header_2_0)(f)
        assert shape==(len(df),len(df))
        for row in range(shape[0]):
            buf=f.read(shape[1]*dtype.itemsize)
            if row in selected:
                if fortran: w[:,selected[row]]=np.frombuffer(buf,dtype)[ix]
                else: w[selected[row]]=np.frombuffer(buf,dtype)[ix]
    assert np.isfinite(w).all()
    # Verify outgoing sign is consistent with the source NT assumption.
    for i,nt in enumerate(table.predictedNt):
        if nt=='acetylcholine': assert (w[i]>=0).all()
        elif nt in ['gaba','glutamate']: assert (w[i]<=0).all()
    table['id']=table.bodyId.astype(str)
    table['source_index']=ix
    table['kind']=np.where(table['class']=='motor neuron','MN',np.where(table.type=='DNg100','DN','CPG'))
    def leg(row):
        region=str(row.somaNeuromere)
        side=str(row.somaSide)
        if row['kind']=='DN': return -1
        if region not in ['T1','T2','T3']: return -1
        return (int(region[1])-1)*2+(0 if side=='LHS' else 1)
    table['leg']=table.apply(leg,axis=1)
    table['region']=table.somaNeuromere.fillna('neck connective')
    table.to_csv(ROOT/'connectome/neurons.csv',index=False)
    np.save(ROOT/'connectome/weights.npy',w,allow_pickle=False)
    warnings.filterwarnings('ignore',category=UserWarning,module='rdata')
    atlas=rdata.read_rda(raw/'MANC.surf.rda')['MANC.surf']
    tissue=rdata.read_rda(raw/'MANC.tissue.surf.rda')['MANC.tissue.surf']
    def surface(obj):
        v=np.asarray(obj['Vertices'][['X','Y','Z']],float)
        regions={str(k):np.asarray(f,dtype=int).tolist() for k,f in obj['Regions'].items()}
        return {'vertices_um':v.tolist(),'regions_one_based':regions}
    dump(ROOT/'connectome/anatomy.json',{'tissue':surface(tissue),'neuropils':surface(atlas),
      'source_commit':ANATOMY,'coordinate_system':'native MANC micrometers; no brain registration',
      'neuron_mesh_mapping':'unavailable: single neurons displayed only in a separate schematic graph',
      'activity_mapping':'region aggregate based on somaNeuromere, not measured arbor occupancy'})
    out={
      'dataset_name':'MANC; Pugliese et al. full-VNC export',
      'dataset_version':'W_20260522_allSynapses / wTable_20260522_allSynapses',
      'underlying_neuprint_version':'not stated in downloaded export; do not infer v1.2.3',
      'upstream_commit':UPSTREAM,'anatomy_commit':ANATOMY,'access_date':'2026-09-17',
      'license':{'connectivity_export':'no explicit repository license found; public redistribution unresolved',
                 'anatomy_package':'malevnc GPL >=3; retain source attribution'},
      'source_files':{k:{'url':v,'sha256':sha(raw/k)} for k,v in FILES.items()},
      'filter':'DNg100; IN17A001; INXXX466; IN16B036; all motor neurons in fl/ml/hl subclasses',
      'orientation':'weights[pre,post]; signed synapse counts; no synapse count threshold',
      'normalization_median_volume':float(df['size'].median()),
      'neuron_count':len(table),'edge_count':int(np.count_nonzero(w)),
      'synapse_count':int(np.abs(w).sum()),'counts_by_kind':table.kind.value_counts().to_dict(),
      'graph_sha256':sha(ROOT/'connectome/weights.npy'),'mesh_sha256':sha(ROOT/'connectome/anatomy.json'),
      'neuron_table_sha256':sha(ROOT/'connectome/neurons.csv'),
      'scope':'VNC motor subgraph with two descending axons; zero reconstructed brain neurons',
      'body_model':'reduced-six-leg-2R-v1.0; original engineering surrogate; not NeuroMechFly',
      'preprocessing_script':'connectome/prepare.py',
      'nt_uncertainty':'predictions, not ground truth; CNS glutamate modeled inhibitory; neuromuscular sign separately engineered',
    }
    dump(ROOT/'connectome_manifest.json',out)
    print(json.dumps({k:out[k] for k in ['neuron_count','edge_count','counts_by_kind']}))
if __name__=='__main__': prepare()



