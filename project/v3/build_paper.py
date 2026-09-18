"""Export evidence tables and Vietnamese PDFs from one immutable campaign."""
from pathlib import Path
import argparse,csv,json,sys,shutil,hashlib,platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
PAPER=ROOT/'paper';FIG=PAPER/'figures';OUT=ROOT/'output/pdf'
FIG.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--run',default='20260918T043824-s0-5816');a=p.parse_args()
folder=ROOT/'runtime/runs'/a.run
read=lambda p:json.loads(p.read_text(encoding='utf8'))
o=read(folder/'optimizer.json');config=read(folder/'config.json');test=read(folder/'test_history.json')[-1]
cps=o['checkpoints'];last=cps[-1]
rows=[]
for cp in cps:
 for part in ['train','validation']:
  for key in ['merry','pool']:
   m=cp[part][key];rows.append(dict(checkpoint=cp['label'],learning_seconds=cp['learning_seconds'],physics_steps=cp['physics_steps'],split=part,piece=key,**m))
with (PAPER/'checkpoint_results.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,3,figsize=(10,3.1),layout='constrained')
for ax,metric in zip(axs,['precision','recall','f1']):
 for key,color in [('merry','#248ba7'),('pool','#b17b26')]:ax.plot([c['learning_seconds']/60 for c in cps],[c['validation'][key][metric] for c in cps],marker='o',color=color,label=key)
 ax.axhline(.85,color='#777777',ls='--',lw=1);ax.set(xlabel='Optimizer minutes',ylabel=metric.title(),ylim=(0,1));ax.grid(alpha=.15)
axs[0].legend(frameon=False);fig.savefig(FIG/'learning.png',dpi=190);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3),layout='constrained')
for part,color in [('train','#8069b4'),('validation','#248ba7')]:ax.plot([c['physics_steps']/1e6 for c in cps],[c[part]['macro_f1'] for c in cps],marker='o',color=color,label=part)
ax.set(xlabel='Cumulative physics steps (million, including evaluation)',ylabel='Macro F1',ylim=(0,.3));ax.legend(frameon=False);ax.grid(alpha=.15);fig.savefig(FIG/'steps.png',dpi=190);plt.close(fig)
table=['| Mốc thực (phút) | Bài | Train F1 | Val P | Val R | Val F1 | Đúng / mục tiêu |','|---|---|---|---|---|---|---|']
for c in cps:
 for k in ['merry','pool']:
  m=c['validation'][k];table.append(f"| {c['learning_seconds']/60:.2f} | {k} | {c['train'][k]['f1']:.3f} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['matched']} / {m['target_notes']} |")
tt=['| Bài | Nốt phát | Đúng | Precision | Recall | F1 | Mục tiêu |','|---|---|---|---|---|---|---|']
for k in ['merry','pool']:
 m=test['results'][k];tt.append(f"| {k} | {m['actual_notes']} | {m['matched']} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['target_notes']} |")
rt=['| Bài / controller | Nốt phát | Đúng | Precision | Recall | F1 | Mục tiêu |','|---|---|---|---|---|---|---|'];replay_metrics={}
for k in ['merry','pool']:
 r=read(folder/f'replays/{k}_trained.json');m=next(m for m in r['metrics'] if m['tolerance_s']==.1);replay_metrics[k]={x:y for x,y in m.items() if x!='matches'}
 rt.append(f"| {k} / trained | {m['actual_notes']} | {m['matched']} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['target_notes']} |")
summary=f"Lượt {a.run}, seed {config['seed']}, gồm {o['generation']} thế hệ hoàn tất và {o['candidate_evaluations']} ứng viên đã đánh giá. Thời gian tối ưu {o['learning_seconds']:.2f} s; đánh giá {o['evaluation_seconds']:.2f} s; tổng thời gian {o['wall_seconds']:.2f} s; {o['physics_steps']:,} bước vật lý. Ngân sách 900 s bị vượt nhẹ vì hoàn tất ứng viên đang chạy. Tham số tốt nhất theo train-monitor không đổi từ mốc 5 đến 15 phút; neural mix cuối bằng {o['best_theta'][14]:.4f}. Tiêu chí 85% chưa đạt."
result=f"Macro-F1 validation tăng từ {cps[0]['validation']['macro_f1']:.3f} lên {last['validation']['macro_f1']:.3f}, nhưng plateau từ mốc 5 phút và macro-F1 test chỉ {test['results']['macro_f1']:.3f}. Precision validation cuối là {last['validation']['merry']['precision']:.3f} và {last['validation']['pool']['precision']:.3f}; chưa đạt mục tiêu >0,85."
text=(PAPER/'manuscript_vi.md').read_text(encoding='utf8')
for tag,value in {'ABSTRACT_RESULT':result,'RUN_SUMMARY':summary,'CHECKPOINT_TABLE':'\n'.join(table),'TEST_TABLE':'\n'.join(tt),'REPLAY_TABLE':'\n'.join(rt),'CONCLUSION_RESULT':result}.items():text=text.replace('{{'+tag+'}}',value)
if '{{' in text:raise RuntimeError('Unresolved manuscript placeholder')
(PAPER/'manuscript_final_vi.md').write_text(text,encoding='utf8')
evidence={'run_id':a.run,'config':config,'optimizer_summary':{k:v for k,v in o.items() if k not in ['pending','rng_state','checkpoints']},'checkpoints':cps,'test':test,'full_replay_metrics':replay_metrics,'note':'One exploratory seed, provisional OMR, private score sequences omitted.'}
(PAPER/'evidence_v3.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf8')
from pdf_renderer import build_pdf
build_pdf(text,OUT/'manuscript_v3_vi.pdf','Fly Piano | Bản thảo v3')
build_pdf((PAPER/'reviewer_vi.md').read_text(encoding='utf8'),OUT/'reviewer_v3_vi.pdf','Fly Piano | Phản biện v3')
print(json.dumps({'output':str(OUT),'run':a.run,'target_met':o['target_met']},ensure_ascii=False))
