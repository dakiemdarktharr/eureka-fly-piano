"""Traceable full-score OMR import; explicitly provisional note accuracy.

Structural corrections come from visual inspection of all 18 supplied pages.
No pitch folding, chord thinning, time stretching or silent note deletion.
"""
from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as ET
import numpy as np
import mido

ROOT=Path(__file__).resolve().parent
CONFIGS={
 'merry':dict(file='song1_merry_go-round_of_life',title='Merry-Go-Round of Life',pages=10,measures=237,
  page_starts=[1,25,53,84,107,132,161,182,209,232],
  tempos={1:109,5:85,28:160,119:109,135:142.5,153:130,168:160,186:75,191:160,224:100,228:160},
  meters={1:(3,4),135:(6,8),151:(3,4),227:(4,4),228:(3,4)},repeat=None),
 'pool':dict(file='song2_in_the_pool_',title='In The Pool',pages=8,measures=69,
  page_starts=[1,13,25,35,42,46,50,64],
  tempos={1:97.5,5:112.5,22:199.5,29:97.5,39:112.5,52:97.5,69:67.5},
  meters={1:(12,8),60:(3,8),61:(12,8)},repeat=(39,42))}

def load_piece(key):
 c=CONFIGS[key];source=ROOT/'scores/verified_omr'/f"{c['file']}.mxl"
 with zipfile.ZipFile(source) as z:
  name=next(n for n in z.namelist() if n.endswith('.xml') and not n.startswith('META'))
  xml=ET.fromstring(z.read(name))
 parts=xml.findall('part');bars={};warnings=[];div=1
 for pi,part in enumerate(parts):
  for me in part.findall('measure'):
   n=int(me.get('number'));cursor=0.;prev=0.;events=[];maxend=0
   dd=me.findtext('attributes/divisions')
   if dd:div=float(dd)
   for item in me:
    if item.tag in ['backup','forward']:
     cursor+=float(item.findtext('duration','0'))/div*(1 if item.tag=='forward' else -1)
    if item.tag!='note':continue
    duration=float(item.findtext('duration','0'))/div
    chord=item.find('chord') is not None
    start=prev if chord else cursor
    if not chord:prev=cursor;cursor+=duration
    maxend=max(maxend,start+duration)
    pitch=item.find('pitch')
    if pitch is None:continue
    midi=12*(int(pitch.findtext('octave'))+1)+{'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[pitch.findtext('step')]+int(float(pitch.findtext('alter','0')))
    events.append(dict(offset=round(start,6),duration=round(duration,6),pitch=midi,staff=item.findtext('staff','1'),voice=item.findtext('voice','1'),part=pi,ties=[t.get('type') for t in item.findall('tie')],grace=item.find('grace') is not None))
   bars.setdefault(n,[]).extend(events)
   meter=c['meters'][max(k for k in c['meters'] if k<=n)];expected=meter[0]*4/meter[1]
   if abs(maxend-expected)>1e-5:warnings.append(dict(measure=n,part=pi,observed_quarters=maxend,expected_quarters=expected,action='Keep notated OMR offsets; anchor next bar to manually checked meter. Review required.'))
 if sorted(bars)!=list(range(1,c['measures']+1)):raise ValueError('Missing or duplicated bar numbering')
 order=list(range(1,c['measures']+1))
 if c['repeat']:
  a,b=c['repeat'];order=order[:b]+list(range(a,b+1))+order[b:]
 notes=[];timeline=[];q=0.;t=0.;open_ties={};tempo=0;tempo_events=[]
 for occurrence,n in enumerate(order):
  bpm=c['tempos'][max(k for k in c['tempos'] if k<=n)]
  if bpm!=tempo:tempo_events.append({'quarter':q,'seconds':t,'quarter_bpm':bpm});tempo=bpm
  numerator,denominator=c['meters'][max(k for k in c['meters'] if k<=n)];barlen=numerator*4/denominator
  page=sum(n>=v for v in c['page_starts'])
  timeline.append(dict(measure=n,occurrence=occurrence,page=page,start=t,end=t+barlen*60/bpm,quarter=q,meter=f'{numerator}/{denominator}',quarter_bpm=bpm))
  for e in bars[n]:
   ident=(e['part'],e['staff'],e['voice'],e['pitch']);start=t+e['offset']*60/bpm;end=start+e['duration']*60/bpm
   if 'stop' in e['ties'] and ident in open_ties and abs(open_ties[ident]['end']-start)<.03:
    old=open_ties[ident];old['end']=end;old['quarter_duration']+=e['duration']
    if 'start' not in e['ties']:open_ties.pop(ident,None)
    continue
   note=dict(id=len(notes),start=round(start,6),end=round(end,6),pitch=e['pitch'],measure=n,occurrence=occurrence,page=page,staff=e['staff'],voice=e['voice'],quarter=round(q+e['offset'],6),quarter_duration=e['duration'],grace=e['grace'])
   notes.append(note)
   if 'start' in e['ties']:open_ties[ident]=note
  q+=barlen;t+=barlen*60/bpm
 notes.sort(key=lambda n:(n['start'],n['pitch']))
 for i,e in enumerate(notes):e['id']=i
 sweep=sorted([(e['start'],1) for e in notes if e['end']>e['start']]+[(e['end'],-1) for e in notes if e['end']>e['start']]);active=0;maximum=0
 for _,delta in sweep:active+=delta;maximum=max(maximum,active)
 pdf=ROOT/'scores/private'/f"{c['file']}.pdf"
 result=dict(id=key,title=c['title'],source_pdf=f"/scores/private/{c['file']}.pdf",source_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),omr_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),pages=c['pages'],measure_count=c['measures'],performed_measures=len(order),duration=max(t,max(e['end'] for e in notes)),notes=notes,bars=timeline,tempos=tempo_events,max_polyphony=maximum,pitch_range=[min(e['pitch'] for e in notes),max(e['pitch'] for e in notes)],status='OMR toàn bài; đã kiểm tra cấu trúc trang, nhịp và tempo. Cao độ/nốt lẻ chưa được xác minh độc lập.',warnings=warnings,
  performance_conventions=['Tempo steps at printed marks; no invented accel./rit./fermata duration.','In The Pool printed dotted-quarter tempi converted to quarter BPM × 1.5.','Printed repeat 39–42 played twice in In The Pool.','Ties merged when pitch/voice and adjoining times agree; pedal/acoustic resonance not biomechanically modeled.','Grace events retained with zero score duration, excluded from sustained-contact targets.','Overfull/underfull OMR bars remain flagged; no global tempo or pitch normalization.'])
 return result

def write_midi(piece,path):
 midi=mido.MidiFile(ticks_per_beat=960);track=mido.MidiTrack();midi.tracks.append(track);events=[]
 for t in piece['tempos']:events.append((round(t['quarter']*960),0,mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(t['quarter_bpm']))))
 for n in piece['notes']:
  if n['quarter_duration']<=0:continue
  events.extend([(round(n['quarter']*960),2,mido.Message('note_on',note=n['pitch'],velocity=75)),(round((n['quarter']+n['quarter_duration'])*960),1,mido.Message('note_off',note=n['pitch'],velocity=0))])
 prev=0
 for tick,_,msg in sorted(events,key=lambda e:(e[0],e[1])):msg.time=max(0,tick-prev);prev=tick;track.append(msg)
 midi.save(path)

if __name__=='__main__':
 out=ROOT/'data';out.mkdir(exist_ok=True)
 for key in CONFIGS:
  p=load_piece(key);(out/f'{key}_score.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8');write_midi(p,out/f'{key}_reference.mid')
  print(key,'notes',len(p['notes']),'duration',p['duration'],'bars',p['performed_measures'],'warnings',len(p['warnings']),'polyphony',p['max_polyphony'],'range',p['pitch_range'])
