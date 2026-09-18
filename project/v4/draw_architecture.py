"""Publication diagram exported as one PNG; arrows are fixed in image coordinates."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def draw(destination):
    fig, ax=plt.subplots(figsize=(16,9))
    fig.subplots_adjust(left=.015,right=.985,bottom=.025,top=.985)
    ax.set(xlim=(0,16),ylim=(0,9));ax.axis('off')
    ink='#213747';teal='#246c68';blue='#315b85'
    def box(x,y,w,h,title,body,fill='#edf4f3'):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.025,rounding_size=.08',facecolor=fill,edgecolor=teal,linewidth=1.3))
        ax.text(x+w/2,y+h*.72,title,ha='center',va='center',fontsize=17,fontweight='bold',color=ink)
        ax.text(x+w/2,y+h*.29,body,ha='center',va='center',fontsize=15,color=ink,linespacing=1.25)
    def arrow(points,dashed=False,color=teal):
        for a,b in zip(points[:-2],points[1:-1]):
            ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=1.6,ls='--' if dashed else '-')
        ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=19,linewidth=1.6,color=color,linestyle='--' if dashed else '-',shrinkA=0,shrinkB=3))
    ax.text(.2,8.6,'A  ĐIỀU KHIỂN TRONG MỘT LƯỢT MÔ PHỎNG',fontsize=19,fontweight='bold',color=ink)
    box(.2,6.6,2.9,1.3,'Mục tiêu nốt','Cao độ, onset, release')
    box(4.,6.6,3.1,1.3,'Lập lịch và IK','Chọn chân; tư thế đích')
    box(8.,6.6,3.1,1.3,'Lệnh servo (θ)','Nội suy tư thế theo mức ấn')
    box(12.,6.6,3.7,1.3,'Cơ thể và bàn phím','MuJoCo; 88 phím vật lý')
    arrow([(3.13,7.25),(3.97,7.25)])
    arrow([(7.13,7.25),(7.97,7.25)])
    arrow([(11.13,7.25),(11.97,7.25)])
    box(4.,4.25,3.1,1.35,'Mạng vận động (θ)','412 neuron; rate model',fill='#eaf0f7')
    arrow([(7.13,5.15),(9.55,5.15),(9.55,6.57)],color=blue)
    ax.text(8.35,5.38,'Mức ấn theo chân',ha='center',fontsize=14,color=blue)
    arrow([(13.85,6.57),(13.85,4.65),(7.13,4.65)],color=blue)
    ax.text(10.45,4.22,'Lực tiếp xúc → phản hồi cảm giác mỗi 2 ms',ha='center',fontsize=14,color=blue)
    ax.text(.2,5.1,'Mục tiêu được đưa vào\nđiều khiển cục bộ trước\nonset tối đa 150 ms.',fontsize=14,color=ink,linespacing=1.3)
    ax.plot([.2,15.7],[3.65,3.65],color='#cbd7df',lw=1)
    ax.text(.2,3.18,'B  TỐI ƯU THAM SỐ GIỮA CÁC LƯỢT MÔ PHỎNG',fontsize=19,fontweight='bold',color=ink)
    box(.2,1.35,2.9,1.3,'Bộ tham số θ','49 tham số bị chặn')
    box(4.,1.35,3.1,1.3,'Chạy hệ ở A','Ghi sự kiện tiếp xúc')
    box(8.,1.35,3.1,1.3,'Chấm và thưởng','Ghép với nốt mục tiêu')
    box(12.,1.35,3.7,1.3,'CEM','10 ứng viên; 3 elite')
    arrow([(3.13,2),(3.97,2)]);arrow([(7.13,2),(7.97,2)]);arrow([(11.13,2),(11.97,2)])
    arrow([(13.85,1.32),(13.85,.55),(1.65,.55),(1.65,1.32)],dashed=True)
    ax.text(7.8,.12,'Cập nhật phân phối tham số cho thế hệ tiếp theo; θ giữ cố định trong mỗi lượt.',ha='center',fontsize=14,color=ink)
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(destination,dpi=300,facecolor='white');plt.close(fig)

if __name__=='__main__':draw(Path(__file__).resolve().parent/'paper/figures/architecture.png')
