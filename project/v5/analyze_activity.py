"""Summarize recorded rates without converting them into biological spikes."""
import csv,json
import numpy as np
from v4_paths import ROOT,STATE,read_json,atomic_json

def main():
 r=read_json(STATE/'preview/skill.json');f=np.fromfile(STATE/'preview/skill.bin',dtype='<f4').reshape(r['frame_count'],r['stride']);a=read_json(ROOT/'assets/manc.json');off,n=r['layout']['neuron_rates'];rates=f[:,off:off+n]
 assert [x['id'] for x in a['neurons']]==r['neuron_ids'];rows=[];regions={}
 for i,cell in enumerate(a['neurons']):
  rows.append(dict(bodyId=cell['id'],cell_type=cell['type'],kind=cell['kind'],region=cell['region'],mean_rate=float(rates[:,i].mean()),max_rate=float(rates[:,i].max()),rate_sd=float(rates[:,i].std()),fraction_frames_active=float((rates[:,i]>1).mean()),geometry_displayed=cell['coordinate_valid']))
 for region in sorted({x['region'] for x in a['neurons']}):
  inds=[i for i,x in enumerate(a['neurons']) if x['region']==region];v=rates[:,inds];regions[region]=dict(neurons=len(inds),mean_rate=float(v.mean()),mean_active_count=float((v>1).sum(1).mean()),peak_active_count=int((v>1).sum(1).max()))
 with (ROOT/'results/neuron_activity.csv').open('w',newline='',encoding='utf8') as out:
  w=csv.DictWriter(out,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 atomic_json(ROOT/'results/region_activity.json',dict(replay_sha256=r['replay_sha256'],duration_s=r['duration'],frames=r['frame_count'],units=r['activity_units'],threshold=1,regions=regions,interpretation='Descriptive activity only. Regions are neuron-table labels, not branch-level neuropil segmentation. High activity does not prove learning, causal necessity, or biological firing.'))
 print(json.dumps(regions))
if __name__=='__main__':main()
