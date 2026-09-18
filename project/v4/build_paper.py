"""Render Vietnamese v4 PDFs and plots directly from saved campaign artifacts."""
from pathlib import Path
import json,csv,sys,argparse,hashlib
from datetime import date
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parent;PAPER=ROOT/'paper';FIG=PAPER/'figures';OUT=ROOT/'output/pdf'
FIG.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf8'))
p=argparse.ArgumentParser();p.add_argument('--run',default='20260918T060329');p.add_argument('--preview',action='store_true');a=p.parse_args()
folder=ROOT/'runtime/runs'/a.run;status=read(folder/'status.json');config=read(folder/'config.json');pilot=read(ROOT/'results/20260918T055453.json');bench=read(ROOT/'research/cpu_benchmark.json')
if status['state']!='completed' and not a.preview:raise RuntimeError('Campaign not complete; use --preview only for layout QA')
cells=status['cells'];done=status['state']=='completed';colors={'adaptive':'#218b7d','frozen':'#b77c28','rewired':'#8d72b8'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(9,3.6),layout='constrained');ax.axis('off')
boxes=[(.02,.65,.22,.22,'Chuỗi nốt mục tiêu\nCửa sổ cục bộ 150 ms'),(.33,.65,.25,.22,'Lập lịch / IK kỹ thuật\n+ hiệu chỉnh ngang được học'),(.02,.12,.22,.25,'Mạng rate 412 neuron\n24 hệ số synapse\n6 hệ số kích thích MN'),(.66,.65,.3,.22,'42 mục tiêu servo\nCơ thể MuJoCo + 88 phím'),(.66,.12,.3,.25,'Sự kiện tiếp xúc vật lý\nGhép nốt một-một'),(.33,.12,.25,.25,'Thưởng episode -> CEM\n10 ứng viên, 3 elite')]
for x,y,w,h,t in boxes:ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.01',facecolor='#e7f1ef',edgecolor='#50938a'));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=9)
for start,end in [((.25,.76),(.32,.76)),((.59,.76),(.65,.76)),((.81,.64),(.81,.38)),((.65,.245),(.59,.245)),((.32,.245),(.25,.245)),((.24,.37),(.67,.65))]:ax.add_patch(FancyArrowPatch(start,end,arrowstyle='->',mutation_scale=13,color='#56716d',lw=1.4))
fig.savefig(FIG/'architecture.png',dpi=190);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.2),layout='constrained');names=[f"CPU {r['workers']} worker" for r in bench['parallel']]+['Mục tiêu 1 năm / giờ'];vals=[r['aggregate_rtf'] for r in bench['parallel']]+[8766]
ax.barh(names,vals,color=['#368f83']*4+['#bc8950']);ax.set_xscale('log');ax.set(xlabel='Giây mô phỏng cộng dồn / giây thực',xlim=(1,30000));ax.grid(axis='x',alpha=.15)
for i,v in enumerate(vals):ax.text(v*1.12,i,f'{v:,.2f}x',va='center',fontsize=8)
fig.savefig(FIG/'throughput.png',dpi=190);plt.close(fig)
for field,filename,xlabel,scale in [('wall_s','learning.png','Thời gian chiến dịch (phút)',60),('physics_steps','sample_efficiency.png','Bước vật lý dùng để tối ưu (triệu)',1e6)]:
 fig,axes=plt.subplots(1,3,figsize=(10,3.1),layout='constrained')
 for seed,ax in enumerate(axes):
  for c in [c for c in cells if c['seed']==seed]:
   ax.plot([h[field]/scale for h in c['history']],[h['metric']['f1'] for h in c['history']],color=colors[c['variant']],label=c['variant'],lw=1.25)
  ax.set(title=f'Seed {seed}',xlabel=xlabel,ylabel='F1 validation',ylim=(0,1));ax.grid(alpha=.15)
 axes[0].legend(frameon=False,fontsize=8);fig.savefig(FIG/filename,dpi=190);plt.close(fig)
train_steps=sum(c['training_steps'] for c in cells);eval_steps=sum(c['evaluation_steps'] for c in cells)
assert train_steps+eval_steps==status['physics_steps']
total_wall=status['elapsed_s']+pilot['status']['elapsed_s'];total_sim=status['aggregate_simulated_s']+pilot['status']['aggregate_simulated_s']
primary=next(c for c in cells if c['seed']==0 and c['variant']=='adaptive')
table=['| Mạng / seed | Train phút mô phỏng | Precision | Recall | F1 | TP / mục tiêu | Warning |','|---|---|---|---|---|---|---|']
for c in cells:
 m=c.get('test') or {};table.append(f"| {c['variant']} / {c['seed']} | {c['training_steps']*.0002/60:.2f} | {m.get('precision',0):.3f} | {m.get('recall',0):.3f} | {m.get('f1',0):.3f} | {m.get('matched','-')} / {m.get('target_notes','-')} | {c.get('solver_warnings','NA')} |")
bt=['| Giai đoạn | Giây thực | Giây mô phỏng mới |','|---|---|---|',f"| V4a thăm dò, 37 tham số | {pilot['status']['elapsed_s']:.2f} | {pilot['status']['aggregate_simulated_s']:.2f} |",f"| V4b, 49 tham số | {status['elapsed_s']:.2f} | {status['aggregate_simulated_s']:.2f} |",f"| Tổng hai lượt | {total_wall:.2f} | {total_sim:.2f} |"]
manifest=read(folder/'replay_manifest.json') if (folder/'replay_manifest.json').exists() else None
passed=sum(bool(c.get('skill_pass') and c.get('sequence_pass')) for c in cells)
summary='; '.join(f"{v}: F1 test trung bình {np.mean([c['test']['f1'] for c in cells if c['variant']==v and c.get('test')]):.3f}" for v in colors) if done else 'Kết quả đang chạy; chưa có test cuối.'
abstract=f"Lượt v4b dùng {status['elapsed_s']:.2f} giây thực, tạo {status['physics_steps']:,} bước vật lý mới, trong đó {train_steps:,} bước dùng để tối ưu. {summary}." if done else 'BẢN XEM BỐ CỤC: chiến dịch chưa hoàn tất; số tạm thời không dùng để kết luận.'
budget=f"Lượt v4a {pilot['config']['run_id']} dừng sau {pilot['status']['elapsed_s']:.2f} s. Lượt v4b {a.run} có trần 3.150 s, bắt đầu với protocol đã sửa và chia 88% ngân sách cho tối ưu. Tổng thực tế hai lượt là {total_wall:.2f} s, {'nằm trong' if total_wall<=3600 else 'vượt'} trần 3.600 s. V4b có {train_steps:,} bước tối ưu và {eval_steps:,} bước đánh giá; RTF toàn chiến dịch v4b là {status['aggregate_rtf']:.3f}. Tổng giây mô phỏng không phải thời gian học của một bộ não duy nhất. Benchmark, phát triển phần mềm và xuất video/replay không nằm trong ngân sách learner này."
learning=f"{summary}. Số thế hệ hoàn tất theo ô nằm trong [{min(c['generation'] for c in cells)}, {max(c['generation'] for c in cells)}]. Đường validation có dao động; checkpoint cuối được chọn bằng validation, không phải điểm cuối đường học. Không sử dụng khác biệt trung bình của ba seed làm chứng cứ ưu thế có ý nghĩa thống kê."
demo=(f"Có {passed}/9 ô vượt đồng thời cổng kỹ năng và chuỗi. Chính sách primary cố định trước là adaptive seed 0. "+('Hai bản nhạc đầy đủ đã được xuất theo cổng chất lượng.' if manifest and manifest['qualified_song_demonstration'] else 'Primary chưa vượt cả hai cổng nên hai bài nhạc đầy đủ bị khóa ở v4. App cung cấp replay kỹ năng để chẩn đoán, không trình bày nó như một buổi biểu diễn thành công. Dữ liệu hai bản nhạc vẫn được giữ nguyên để đánh giá sau.'))
conclusion=f"V4 triển khai tăng tốc CPU có kiểm tra tương đương và một pipeline học/đánh giá có ngân sách. {summary}. Mục tiêu một năm mô phỏng trong một giờ chưa đạt; probe GPU không tương thích noslip. Kết quả là đánh giá của một bộ điều khiển lai có hỗ trợ hình học trong phạm vi synthetic hẹp. Cần sửa/kiểm chứng cơ học tiếp xúc và bổ sung baseline, test chuyển giao trước khi đưa ra kết luận rộng hơn."
editorial=f"Phiên bản này là nghiên cứu thăm dò: {summary}. Tổng learner wall time của hai lượt: {total_wall/60:.2f} phút. Số ô đạt cả skill và sequence gate: {passed}/9. Chưa đủ bằng chứng để gọi manuscript là sẵn sàng nộp Q2; các điểm còn mở bên dưới phải được giữ trong paper."
checkpoint_rows=['| Mốc thực (phút) | Seed | P trung bình | R trung bình | F1 trung bình | F1 min-max | Trễ tối đa (s) |','|---|---|---|---|---|---|---|']
for minute in [5,15,30,45]:
 if status['elapsed_s']<minute*60:continue
 selected=[]
 for c in cells:
  if c['variant']!='adaptive':continue
  eligible=[h for h in c['history'] if h['wall_s']<=minute*60]
  if eligible:selected.append(eligible[-1])
 if selected:
  mm=[h['metric'] for h in selected];checkpoint_rows.append(f"| {minute} | {len(mm)} | {np.mean([m['precision'] for m in mm]):.3f} | {np.mean([m['recall'] for m in mm]):.3f} | {np.mean([m['f1'] for m in mm]):.3f} | {min(m['f1'] for m in mm):.3f}-{max(m['f1'] for m in mm):.3f} | {max(minute*60-h['wall_s'] for h in selected):.1f} |")
values={'DATE':str(date.today()),'ABSTRACT_RESULTS':abstract,'BUDGET_RESULTS':budget,'BUDGET_TABLE':'\n'.join(bt),'LEARNING_RESULTS':learning,'TEST_TABLE':'\n'.join(table),'DEMO_RESULTS':demo,'CONCLUSION':conclusion,'EDITORIAL':editorial,'CHECKPOINT_TABLE':'\n'.join(checkpoint_rows)}
sys.path.insert(0,str(ROOT));import pdf_renderer
pdf_renderer.PAPER=PAPER
for stem,title in [('manuscript','Fly Piano v4 - ban thao nghien cuu'),('reviewer','Fly Piano v4 - phan bien va huong xu ly')]:
 text=(PAPER/f'{stem}_vi.md').read_text(encoding='utf8')
 for key,value in values.items():text=text.replace('{{'+key+'}}',value)
 if '{{' in text:raise RuntimeError('Unresolved placeholder')
 if not done:text='BẢN XEM BỐ CỤC - THÍ NGHIỆM ĐANG CHẠY\n\n'+text
 (PAPER/f'{stem}_final_vi.md').write_text(text,encoding='utf8');pdf_renderer.build_pdf(text,OUT/f'{stem}_v4_vi.pdf',title)
rows=[]
for c in cells:
 for h in c['history']:rows.append(dict(seed=c['seed'],variant=c['variant'],generation=h['generation'],campaign_wall_s=h['wall_s'],training_physics_steps=h['physics_steps'],**h['metric']))
with (PAPER/'learning.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
evidence=dict(config=config,status=status,pilot_summary={k:v for k,v in pilot['status'].items() if k!='cells'},benchmark=bench,replay_manifest=manifest,total_learner_wall_s=total_wall,training_steps=train_steps,evaluation_steps=eval_steps,scope='Exploratory; no unqualified biological or Q2-acceptance claim')
(PAPER/'evidence_v4.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf8');print(OUT)
