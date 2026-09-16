"""Replay serialization: values sampled from telemetry, never synthesized."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulation.model import ROOT,MotorNetwork
from connectome.prepare import dump,sha

def replay(run_id,fps=25,run_root=None):
    path=(Path(run_root) if run_root else ROOT/'data/runs')/run_id
    meta=json.loads((path/'metadata.json').read_text());metrics=json.loads((path/'metrics.json').read_text())
    if sha(path/'telemetry.npz')!=meta['telemetry_sha256']:raise ValueError('Telemetry checksum mismatch')
    df=pd.read_csv(ROOT/'connectome/neurons.csv',keep_default_na=False)
    if sha(ROOT/'connectome/weights.npy')!=meta['graph_sha256']: raise ValueError('Graph checksum mismatch')
    model=MotorNetwork(meta['seed'],meta['variant'],meta['dt'])
    is_rnn=meta['variant']=='rnn'
    w=model.rw.T if is_rnn else model.w.toarray().T/.03
    if is_rnn:
        df['id']=['rnn_slot_'+str(i) for i in range(len(df))]
        df['type']='synthetic reservoir state';df['region']='not anatomical';df['predictedNt']='not applicable';df['predictedNtProb']=''
    neurons=[]
    for i,row in df.iterrows():
        neurons.append({'id':str(row.id),'type':row.type,'kind':row.kind,'region':row.region,'leg':int(row.leg),
          'nt':row.predictedNt,'confidence':(float(row.predictedNtProb) if str(row.predictedNtProb) else None),'source':('synthetic RNN' if is_rnn else 'counterfactual rewired graph' if meta['variant']=='randomized' else 'measured graph / modeled rate'),
          'downstream':[{'id':str(df.iloc[j].id),'signed_synapses':float(w[i,j]),'units':('reservoir weight' if is_rnn else 'signed synapse count')} for j in np.flatnonzero(w[i])]})
    from collections import deque
    adjacency=[np.flatnonzero(w[i]).tolist() for i in range(len(w))]
    starts=np.flatnonzero(df.kind=='DN').tolist()
    def upstream(target):
        queue=deque((s,[s]) for s in starts);seen=set(starts)
        while queue:
            node,trace=queue.popleft()
            if node==target:return [str(df.iloc[i].id) for i in trace]
            for nxt in adjacency[node]:
                if nxt not in seen:seen.add(nxt);queue.append((nxt,trace+[nxt]))
        return None
    for contact in meta['contacts']:
        candidates=np.flatnonzero(df.bodyId.astype(str)==str(contact['responsible_mn_id']))
        if len(candidates):
            index=int(candidates[0]);contact['structural_upstream_path']=upstream(index)
            if is_rnn:contact['responsible_mn_id']=str(df.iloc[index].id)
        contact['path_interpretation']='structural reachability only; not causal attribution'
    with np.load(path/'telemetry.npz') as z:
        ix=np.unique(np.minimum((np.arange(0,meta['duration'],1/fps)/meta['dt']).round().astype(int),len(z['time'])-1))
        frames={k:z[k][ix].round(5).tolist() for k in ['time','rates','task','q','force','actual','target','limb']}
        frames['raw_index']=ix.tolist()
        return {'metadata':meta,'metrics':metrics,'neurons':neurons,'frames':frames,'key_x':z['key_x'].tolist(),
          'key_height':float(z['key_height']),'hips':z['hips'].tolist(),
          'legend':{'neuron_rate_hz':[0,250],'region_mean_rate_hz':[0,20],'task_relay':[0,1]},
          'anatomy_disclosure':'Real MANC regional mesh. Single neurons have graph positions, not anatomical positions. No brain neuron simulation.',
          'pathway_disclosure':'Edges match the variant-specific dynamics. Anatomical identities do not apply to RNN slots. Activity is not proof of causal propagation.',
          'timestamp_convention':'time t labels input/contact evaluation; logged rates and q are post-update states at nominal t+dt (2 ms in main batch)',
          'body_driver':('alternative controller; neural rates are shadow telemetry' if meta['variant'] in ['direct','hand_cpg','sequence_specific'] else 'equal-weight MN population readout')}
def export(run_id):
    p=ROOT/'app/replays'/f'{run_id}.json';dump(p,replay(run_id));return p
if __name__=='__main__':
    export(sys.argv[1] if len(sys.argv)>1 else 'B1_novel_full_s00')



