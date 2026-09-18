"""Render revised v4 narrative and v5 paper without recomputing locked v4 data."""
from pathlib import Path
import hashlib,json,shutil,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from matplotlib.font_manager import FontProperties
R=Path(__file__).resolve().parent;V4=R.parent/'v4';P=R/'paper';F=P/'figures';F.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(V4));import pdf_renderer as pdf
font=FontProperties(fname='C:/Windows/Fonts/arial.ttf')
def diagram():
 fig,ax=plt.subplots(figsize=(11,4.5));fig.patch.set_facecolor('white');ax.set(xlim=(0,11),ylim=(0,4.5));ax.axis('off')
 boxes=[(.25,2.55,2.1,1.1,'100 mục tiêu\ncao độ + thời gian'),(3,2.55,2.1,1.1,'Lập lịch + IK\nvà mạng 412 neuron'),(5.75,2.55,2.1,1.1,'42 servo\nMuJoCo → tiếp xúc'),(8.5,2.55,2.1,1.1,'Ghép nốt một–một\nP / R / F1'),(3,0.45,4.85,1.05,'CEM → tìm kiếm tọa độ → CEM\nValidation chọn checkpoint; test chỉ đánh giá')]
 for x,y,w,h,label in boxes:
  ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04',linewidth=1.2,edgecolor='#28605f',facecolor='#f0f6f5'))
  ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontproperties=font,fontsize=11,linespacing=1.7,color='#182c3a')
 for a,b in [((2.4,3.1),(2.94,3.1)),((5.15,3.1),(5.69,3.1)),((7.9,3.1),(8.44,3.1)),((4.05,1.57),(4.05,2.47))]:
  ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,linewidth=1.5,color='#28605f'))
 ax.plot([9.55,9.55,7.95],[2.48,.98,.98],color='#ad7346',lw=1.5)
 ax.add_patch(FancyArrowPatch((8.05,.98),(7.91,.98),arrowstyle='-|>',mutation_scale=15,linewidth=1.5,color='#ad7346'))
 ax.text(4.15,1.95,'tham số',fontproperties=font,fontsize=10,color='#28605f')
 ax.text(9.68,1.7,'điểm',fontproperties=font,fontsize=10,color='#ad7346')
 ax.text(.25,4.1,'Đường tín hiệu và cập nhật giữa các episode',fontproperties=font,fontsize=14,color='#182c3a')
 fig.savefig(F/'protocol.png',dpi=220,bbox_inches='tight');plt.close(fig)

def revise_v4():
 files=[V4/'paper/evidence_v4.json',V4/'paper/learning.csv']
 hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}
 for name in ['manuscript_vi.md','manuscript_final_vi.md']:
  p=V4/'paper'/name;s=p.read_text(encoding='utf8')
  old='Sau khi khóa kết quả v4b, một lượt bổ sung luyện trực tiếp hai bài được khởi chạy với ngân sách tối đa 60 phút mỗi bài.'
  start=s.find(old)
  if start>=0:
   end=s.find('\n\n',start)
   s=s[:start]+'Sau khi khóa kết quả v4b, các lượt luyện bài bổ sung được phát triển riêng; ngân sách ban đầu 60 phút mỗi bài sau đó tăng lên 120 phút. V5 chuyển episode sang đúng 100 sự kiện và bổ sung giai đoạn kỹ năng trước hai nhánh bài nhạc. Những lượt này không nằm trong bảng kết quả v4b, không thay đổi mẫu số của thí nghiệm đã khóa và không phải kiểm tra khái quát hóa sang bài mới.'+s[end:]
  marker='### Cập nhật tài liệu và protocol ngày 18/09/2026'
  if marker not in s:
   insert='''### Cập nhật tài liệu và protocol ngày 18/09/2026

FlyGM v3 mô tả khởi tạo bằng imitation learning rồi tinh chỉnh PPO [3], nên không nên giới hạn mô tả công trình này ở imitation đơn thuần. FLYNN dùng DAgger trong điều hướng robot [10]; cả hai không phải bằng chứng trực tiếp cho tác vụ piano của mô hình hiện tại. ENOMAD gợi ý phối hợp tìm kiếm toàn cục và cục bộ [11]. CANTABILE nhấn mạnh cần kiểm soát độ phủ onset để tránh tăng điểm bằng cách bỏ nốt [12]. Các hướng này được dùng để thiết kế protocol v5 riêng, chưa phải kết quả cải thiện của v4.

V5 bổ sung mục tiêu P ≥80% đi kèm R ≥60%, các chuỗi validation/test riêng gồm 100 nốt mỗi chuỗi và chuyển CEM sang tìm kiếm tọa độ khi plateau. Phép thử teacher cơ học chưa đạt yêu cầu: trên 100 mục tiêu seed 82001, ép gate tối đa hoặc chuyển đích IK sang điểm thấp nhất của mesh không tăng số nốt khớp, nhưng tăng bấm thừa. Vì vậy chưa triển khai imitation từ teacher này. Các thất bại chẩn đoán không cho phép kết luận về giới hạn học của ruồi sinh học.

'''
   s=s.replace('## 8. Kết luận',insert+'## 8. Kết luận')
   s+='\n\n[10] [Wang và Chen. FLYNN. arXiv:2607.00025, 2026, preprint](https://arxiv.org/html/2607.00025).\n\n[11] [Reinforcement learning in densely recurrent biological networks. iScience, trực tuyến 15/12/2025](https://www.cell.com/iscience/fulltext/S2589-0042(25)02697-5).\n\n[12] [Kim và cộng sự. CANTABILE. arXiv:2609.18213, 16/09/2026, preprint](https://arxiv.org/abs/2609.18213).\n'
  s=s.replace('arXiv:2602.17997, 2026, preprint](https://arxiv.org/abs/2602.17997)','arXiv:2602.17997v3, 14/06/2026, preprint](https://arxiv.org/html/2602.17997v3)')
  p.write_text(s,encoding='utf8')
 old=V4/'output/pdf/manuscript_v4_vi.pdf';backup=R/'runtime/paper_backup/manuscript_v4_before_20260918.pdf';backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():shutil.copy2(old,backup)
 pdf.PAPER=V4/'paper';pdf.build_pdf((V4/'paper/manuscript_final_vi.md').read_text(encoding='utf8'),old,'Fly Piano | v4 · cập nhật thảo luận',reference_page_break=False)
 assert hashes=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}
 return hashes

if __name__=='__main__':
 diagram();shutil.copy2(R/'qa/neural.jpg',F/'anatomy.jpg')
 hashes=revise_v4();pdf.PAPER=P;(R/'output/pdf').mkdir(parents=True,exist_ok=True)
 pdf.build_pdf((P/'manuscript_vi.md').read_text(encoding='utf8'),R/'output/pdf/manuscript_v5_vi.pdf','Fly Piano | v5 · phương pháp và chẩn đoán')
 (R/'results/paper_build.json').write_text(json.dumps(dict(v4_locked_hashes=hashes,v5_results_status='Diagnostics only; long-run results pending'),indent=2),encoding='utf8')
 print('Rendered revised v4 and new v5; locked v4 numerical evidence unchanged.')
