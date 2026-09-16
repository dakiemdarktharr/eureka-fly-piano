"""Authorized local WAV/event input. No downloading or copying copyrighted audio.
WAV extraction is a crude mono spectral-peak/onset baseline, not polyphonic transcription.
"""
from pathlib import Path
import json,argparse,hashlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft,find_peaks

def wav_events(path,nkeys=8):
    sr,x=wavfile.read(path);x=x.astype(float)
    if x.ndim>1:x=x.mean(1)
    x/=max(1,abs(x).max())
    f,t,z=stft(x,sr,nperseg=2048,noverlap=1536);mag=abs(z);flux=np.maximum(0,np.diff(mag,axis=1)).sum(0)
    peaks,_=find_peaks(flux,prominence=max(1e-9,np.std(flux)),distance=max(1,round(.12/(t[1]-t[0]))))
    events=[]
    for i,p in enumerate(peaks):
        hz=float(f[np.argmax(mag[:,p+1])]);midi=69+12*np.log2(max(hz,1)/440)
        events.append({'event_id':i,'time':float(t[p+1]),'key':int(round(midi))%nkeys,'estimated_midi':float(midi),'frequency_hz':hz,'onset_strength':float(flux[p]),'hold':.13})
    return {'events':events,'method':'spectral-flux peaks + dominant STFT bin; modulo-key reduction',
      'limitations':'No polyphonic separation, beat inference validation, or composer-specific reconstruction. Inspect every event before use.',
      'source_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'source_filename':Path(path).name,'nkeys':nkeys,'audio_redistributed':False}
def midi_events(path,nkeys=8):
    import mido
    elapsed=0.;raw=[]
    for message in mido.MidiFile(path):
        elapsed+=message.time
        if message.type=='note_on' and message.velocity>0:
            raw.append({'time':elapsed,'midi':message.note,'velocity':message.velocity})
    # Explicit monophonic reduction: retain the highest note in each 20 ms cluster.
    reduced=[]
    for event in raw:
        if reduced and event['time']-reduced[-1]['time']<.02:
            if event['midi']>reduced[-1]['midi']:reduced[-1]=event
        else:reduced.append(event)
    return {'events':[{'event_id':i,'time':e['time'],'key':e['midi']%nkeys,'hold':.13} for i,e in enumerate(reduced)],
      'original_note_ons':raw,'method':'MIDI tempo-map decoding; highest note per 20 ms cluster; pitch modulo keyboard size',
      'discarded_note_count':len(raw)-len(reduced),'source_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
      'source_filename':Path(path).name,'nkeys':nkeys,'audio_redistributed':False,
      'limitations':'Explicit lossy monophonic reduction, not a faithful polyphonic piano rendition.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');p.add_argument('--keys',type=int,choices=[4,8,16],default=8);a=p.parse_args()
    result=(midi_events if Path(a.input).suffix.lower() in ['.mid','.midi'] else wav_events)(a.input,a.keys)
    Path(a.output).write_text(json.dumps(result,indent=2),encoding='utf8')
