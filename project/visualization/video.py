"""Deterministic telemetry-to-video renderer with synthetic contact sonification."""
from pathlib import Path
import sys,json,subprocess,wave,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulation.model import ROOT
from visualization.replay import replay
from connectome.prepare import dump,sha

W,H=1280,720
COLORS=['#67d9c7','#d59be2','#77b5e2','#e0bc70','#b1d17a','#e58b80']
def font(size):
    for p in ['C:/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default(size=size)
FONTS={s:font(s) for s in [10,12,14,16,20,27]}
def label(d,xy,txt,size=14,fill='#a4bacb'):d.text(xy,str(txt),font=FONTS[size],fill=fill)
def color(rate,maximum=250):
    v=float(np.clip(rate/maximum,0,1));return (int(35+185*v),int(75+175*v),int(125+75*(1-v)))

class Renderer:
    def __init__(self,data):
        self.data=data;self.atlas=json.loads((ROOT/'connectome/anatomy.json').read_text())
        self.neurons=data['neurons'];self.f=data['frames'];self.region_points=[]
        surf=self.atlas['neuropils'];verts=np.array(surf['vertices_um'])
        for name,faces in surf['regions_one_based'].items():
            pts=verts[np.unique(np.array(faces)[::30].ravel())-1]
            reg=next((s for s in ['T1','T2','T3'] if s in name),'neck connective')
            ids=[i for i,n in enumerate(self.neurons) if n['region']==reg]
            p=np.column_stack([235+(pts[:,0]-210)*.58+(pts[:,1]-210)*.12,130+pts[:,2]*.40])
            self.region_points.append((p,ids))
        rates=np.array(self.f['rates']);v=np.clip(rates.T/250,0,1)
        self.raster=Image.fromarray(np.stack([30+220*v,35+210*v,60+100*v],axis=2).astype('uint8')).resize((788,120))
    def frame(self,i):
        data=self.data;f=self.f;meta=data['metadata'];t=f['time'][i]
        im=Image.new('RGB',(W,H),'#071018');d=ImageDraw.Draw(im)
        label(d,(26,16),'EUREKA / MOTOR CONTROL OBSERVATORY',12,'#7da7bd');label(d,(26,36),'Measured wiring. Modeled movement.',27,'#e6edf2')
        label(d,(770,24),meta['run_id'],16,'#6be2c2');label(d,(770,48),f't = {t:5.3f} s  |  seed {meta["seed"]}  |  raw frame {f["raw_index"][i]}',14)
        for box in [(22,86,450,422),(466,86,850,422),(866,86,1258,422),(22,438,838,609),(854,438,1258,609)]:d.rounded_rectangle(box,8,fill='#0c1923',outline='#294050')
        label(d,(36,99),'01  MANC VNC / anatomical regions',14)
        r=np.array(f['rates'][i])
        for pts,ids in self.region_points:
            c=color(r[ids].mean() if ids else 0,20)
            for x,y in pts:
                if 40<x<435 and 125<y<393:d.point((int(x),int(y)),fill=c)
        label(d,(35,392),'Fixed region mean: 0-20 Hz | soma-region grouping',12)
        label(d,(480,99),'02  Six-leg 2R dynamical body',14)
        sx=lambda x:660+x*210;sy=lambda z:145-z*240
        xs=data['key_x'];key=f['target'][i];force=f['force'][i];actual=f['actual'][i]
        for k,x in enumerate(xs):
            kw=abs(xs[1]-xs[0])*180*.8
            c='#64e6b5' if any(v>.04 and actual[l]==k for l,v in enumerate(force)) else '#d7af62' if k==key else '#9aafba'
            d.rectangle([sx(x)-kw/2,sy(data['key_height']),sx(x)+kw/2,sy(data['key_height'])+22],fill=c)
            label(d,(sx(x)-4,sy(data['key_height'])+23),k,10)
        d.ellipse((590,129,723,159),fill='#57748c');d.ellipse((718,129,747,155),fill='#7693aa')
        for l in range(5,-1,-1):
            hip=np.array(data['hips'][l]);q=f['q'][i][l];knee=hip+.65*np.array([np.cos(q[0]),np.sin(q[0])]);foot=knee+.65*np.array([np.cos(sum(q)),np.sin(sum(q))])
            pts=[(sx(p[0]),sy(p[1])) for p in [hip,knee,foot]];d.line(pts,fill=COLORS[l],width=3);x,y=pts[-1];d.ellipse((x-4,y-4,x+4,y+4),fill='#76ffbb' if force[l]>.04 else COLORS[l]);label(d,(pts[1][0]+3,pts[1][1]),['LF','RF','LM','RM','LH','RH'][l],10,COLORS[l])
        label(d,(480,394),'Gold target / green physical contact',12)
        label(d,(881,99),'03  Event and model state',14)
        contacts=[c for c in meta['contacts'] if c['time']<=t];contact=contacts[-1] if contacts else None
        lines=[f'Condition: {meta["condition"]}',f'Variant: {meta["variant"]}',f'Expected key: {key if key>=0 else "none"}',f'Actual contacts: {sum(x>.04 for x in force)}',f'Last contact: key {contact["key"]} / {contact["time"]:.3f} s' if contact else 'Last contact: none',f'Contact error: {contact["timing_error_s"]:+.3f} s' if contact and contact['timing_error_s'] is not None else 'Contact error: N/A',f'Readout MN: {contact["responsible_mn_id"]}' if contact else 'Readout MN: N/A',f'Force: {contact["force"]:.3f} model units' if contact else 'Force: 0 model units','Brain neurons: not included','Task relay / body decoder: engineered']
        for j,line in enumerate(lines):label(d,(882,132+j*24),line,14,'#dac297' if j>=8 else '#c2d3df')
        label(d,(35,450),'04  Rate raster (not spikes) / all 412 measured neurons',14)
        im.paste(self.raster,(36,478));d.line((36+i/(len(f['time'])-1)*788,478,36+i/(len(f['time'])-1)*788,598),fill='#ffffff',width=2)
        label(d,(869,451),'05  Structural DN / CPG core',14)
        ids=[10093,10707,11751,13905];idx=[next(j for j,n in enumerate(self.neurons) if n['id']==str(x)) for x in ids]
        ps=[(894,503),(1000,503),(1110,503),(1110,560)]
        for a,b in [(0,1),(1,2),(2,3),(3,1)]:
            if any(edge['id']==str(ids[b]) for edge in self.neurons[idx[a]]['downstream']): d.line([ps[a],ps[b]],fill='#5c99a9' if a!=3 else '#d787a7',width=2)
        for j,p in enumerate(ps):
            d.ellipse((p[0]-8,p[1]-8,p[0]+8,p[1]+8),fill=color(r[idx[j]]));label(d,(p[0]-24,p[1]+12),ids[j],10)
        label(d,(868,588),'Graph positions | rates: 0-250 Hz | not causal tracing',10)
        label(d,(27,625),meta['hypothesis'][:145],14,'#8cdbc9')
        label(d,(27,650),('SHADOW NEURAL TELEMETRY: body is driven by the alternative controller.' if meta['variant'] in ['direct','hand_cpg','sequence_specific'] else 'Reduced VNC feasibility model. No brain simulation, learned primitives, or biological piano claim.'),12,'#d3b587')
        label(d,(27,675),f'Git {meta["git_commit"][:12]} | {meta["dataset_version"]} | config {meta["config_sha256"][:16]}',10)
        label(d,(27,692),f'Telemetry SHA256 {meta["telemetry_sha256"]} | all graphics sampled from recorded data',10)
        return im

def render(run_ids,name,fps=25,run_root=None):
    folder=ROOT/'videos';folder.mkdir(exist_ok=True);tmp=ROOT/'tmp/video';tmp.mkdir(parents=True,exist_ok=True)
    replays=[replay(r,fps,run_root) for r in run_ids];duration=sum(r['metadata']['duration'] for r in replays);sr=22050;sound=np.zeros(round(duration*sr));offset=0
    for r in replays:
        for c in r['metadata']['contacts']:
            freq=261.6256*2**(c['key']/12);n=int(.23*sr);x=np.arange(n)/sr;waveform=.14*np.sin(2*np.pi*freq*x)*np.exp(-x*17)
            start=round((offset+c['time'])*sr);end=min(len(sound),start+n);sound[start:end]+=waveform[:end-start]
        offset+=r['metadata']['duration']
    wav=tmp/(name+'.wav')
    with wave.open(str(wav),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes((np.clip(sound,-1,1)*32767).astype('<i2').tobytes())
    output=folder/(name+'.mp4')
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',str(wav),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-shortest','-movflags','+faststart',str(output)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for j,r in enumerate(replays):
            renderer=Renderer(r)
            for i in range(len(r['frames']['time'])):
                im=renderer.frame(i);proc.stdin.write(im.tobytes())
                if j==0 and i==min(45,len(r['frames']['time'])-1):im.save(folder/(name+'_preview.png'))
    finally:proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('ffmpeg failed')
    dump(folder/(name+'.metadata.json'),{'run_ids':run_ids,'fps':fps,'duration':duration,'audio':'synthetic sine tones from actual physical contacts; no copyrighted audio','source_metadata':[r['metadata'] for r in replays],'video_sha256':sha(output)})
    print(output,flush=True)
if __name__=='__main__':
    render(['B1_novel_full_s00'],'controlled_motor_tests')
    render(['B1_novel_full_s00','B1_novel_no_cpg_s00','B1_novel_direct_s00'],'ablation_comparison')


