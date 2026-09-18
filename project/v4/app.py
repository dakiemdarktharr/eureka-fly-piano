"""Local-only v4 app: bounded jobs, protected mutations, allowlisted files."""
import argparse,json,os,re,secrets,subprocess,sys,threading,webbrowser,multiprocessing
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,unquote
from pathlib import Path
from v4_paths import ROOT,V2,STATE,PROJECT,read_json
TOKEN=secrets.token_urlsafe(32);LOCK=threading.Lock();CHILD=None
RID=re.compile(r'^[0-9]{8}T[0-9]{6}$')

def readiness():
    required=[PROJECT/'connectome/weights.npy',PROJECT/'connectome/neurons.csv',V2/'data/ik_cache.npz',V2/'data/merry_score.json',V2/'data/pool_score.json',V2/'assets/fly_model/piano_fly.xml']
    missing=[str(p.relative_to(PROJECT)) for p in required if not p.is_file()]
    return {'ready':not missing,'missing':missing}

def latest():
    p=STATE/'latest.json'
    if not p.exists():return None,None
    rid=read_json(p)['run_id']
    if not RID.fullmatch(rid):raise ValueError('Invalid campaign id')
    folder=STATE/'runs'/rid
    return folder,read_json(folder/'status.json')
def alive(s):
    import psutil
    return bool(s and s['state'] in ['training','testing','exporting'] and psutil.pid_exists(s['pid']))
def replay_folder():
    folder,s=latest()
    if folder and (folder/'replay_manifest.json').exists():return folder/'replays',read_json(folder/'replay_manifest.json')
    return STATE/'preview',{'qualified_song_demonstration':False,'preview':True,'items':[{'piece':'skill'}]}
def state():
    folder,s=latest();_,manifest=replay_folder()
    if s and s['state'] in ['training','testing','exporting'] and not alive(s):s['state']='interrupted'
    bench=ROOT/'research/cpu_benchmark.json'
    return dict(csrf=TOKEN,readiness=readiness(),campaign=s,replay=manifest,benchmark=read_json(bench) if bench.exists() else None)
def launch(minutes,workers):
    global CHILD
    command=[sys.executable,'--worker','songs','--minutes',str(minutes),'--workers',str(workers)]
    if not getattr(sys,'frozen',False):command.insert(1,str(ROOT/'app.py'))
    STATE.mkdir(parents=True,exist_ok=True)
    with (STATE/'worker.log').open('ab') as log:
        CHILD=subprocess.Popen(command,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def list_directory(self,path):self.send_error(404)
    def json(self,value,status=200):
        b=json.dumps(value,ensure_ascii=False,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store');super().end_headers()
    def route(self,path):
        if path=='/':return ROOT/'ui/index.html'
        if path in ['/ui/app.js','/ui/style.css','/ui/dashboard.js']:return ROOT/path[1:]
        if path in ['/ui/vendor/three.module.js','/ui/vendor/three.core.js','/ui/vendor/OrbitControls.js']:return V2/path[1:]
        if path in ['/assets/scene.json','/assets/brain.json','/assets/attribution.json']:return V2/path[1:]
        if re.fullmatch(r'/replay/(skill|merry|pool)\.(json|bin)',path):return replay_folder()[0]/Path(path).name
        if re.fullmatch(r'/data/(merry|pool)_(score\.json|reference\.mid)',path):return V2/path[1:]
        if re.fullmatch(r'/scores/private/song[12]_[a-z0-9_\-]+\.pdf',path):return V2/path[1:]
        if path=='/paper/manuscript.pdf':return ROOT/'output/pdf/manuscript_v4_vi.pdf'
        if path=='/paper/reviewer.pdf':return ROOT/'output/pdf/reviewer_v4_vi.pdf'
        return None
    def local_host(self):
        try:
            host=urlsplit('http://'+self.headers.get('Host',''))
            return host.hostname in ['127.0.0.1','localhost','::1'] and host.username is None and not host.path and (host.port is None or 0<host.port<65536)
        except ValueError:return False
    def do_GET(self):
        if not self.local_host():return self.json({'error':'Host rejected'},403)
        path=unquote(urlsplit(self.path).path)
        if path=='/api/state':return self.json(state())
        if path=='/api/health':return self.json({'ok':True,'version':4,**readiness()})
        if path=='/api/export':
            folder,s=latest();return self.json({'config':read_json(folder/'config.json'),'status':s} if folder else {})
        file=self.route(path)
        if file is None or not file.is_file():return self.send_error(404)
        self._file=file;return super().do_GET()
    def translate_path(self,path):return str(getattr(self,'_file',ROOT/'missing'))
    def do_POST(self):
        if not self.local_host():return self.json({'error':'Host rejected'},403)
        host=self.headers.get('Host','');origin=self.headers.get('Origin')
        if origin and origin!=f'http://{host}':return self.json({'error':'Origin rejected'},403)
        if not secrets.compare_digest(self.headers.get('X-FlyPiano-Token',''),TOKEN):return self.json({'error':'Token rejected'},403)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<=size<=2048:raise ValueError('Request too large')
            body=json.loads(self.rfile.read(size) or b'{}')
            with LOCK:
                folder,s=latest()
                if self.path=='/api/train':
                    if not readiness()['ready']:return self.json({'error':'Missing private inputs: '+', '.join(readiness()['missing'])},400)
                    if alive(s) or (CHILD and CHILD.poll() is None):return self.json({'error':'A campaign is already running'},409)
                    minutes=float(body.get('minutes',60));workers=int(body.get('workers',4))
                    if not 0<minutes<=60 or workers not in range(1,7):raise ValueError('Budget 0..60 minutes, 1..6 workers')
                    launch(minutes,workers);return self.json({'started':True})
                if self.path=='/api/stop':
                    if not alive(s):return self.json({'error':'No running campaign'},409)
                    (folder/'stop.request').write_text('User requested stop');return self.json({'stopping':True})
            return self.json({'error':'Unknown route'},404)
        except (ValueError,TypeError,OSError) as e:return self.json({'error':str(e)},400)

def main():
    multiprocessing.freeze_support();p=argparse.ArgumentParser();p.add_argument('--host',choices=['127.0.0.1','0.0.0.0'],default='127.0.0.1');p.add_argument('--port',type=int,default=8878);p.add_argument('--no-browser',action='store_true');p.add_argument('--worker',choices=['train','songs','verify']);p.add_argument('--minutes',type=float,default=60);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    if a.worker=='verify':
        from engine import Engine,INITIAL
        from v4_paths import atomic_json
        e=Engine();notes,d=e.synthetic(80002,count=1);r=e.rollout(INITIAL,notes,d)
        atomic_json(STATE/'bundle_verify.json',{'ok':r['solver_warnings']==0,'physics_steps':r['physics_steps'],'finite':True,'training':False,'parameters':len(INITIAL)})
        return
    if a.worker=='songs':
        from train_songs import run
        run(a.minutes,a.workers);return
    if a.worker:
        from train import run,export
        folder=run(a.minutes,a.workers);export(folder.name);return
    STATE.mkdir(parents=True,exist_ok=True)
    if sys.stdout is None:sys.stdout=(STATE/'app.log').open('a',encoding='utf8',buffering=1)
    if sys.stderr is None:sys.stderr=sys.stdout
    try:server=ThreadingHTTPServer((a.host,a.port),Handler)
    except OSError:
        from urllib.request import urlopen
        try:
            with urlopen(f'http://127.0.0.1:{a.port}/api/health',timeout=2) as r:health=json.load(r)
            if health.get('version')!=4:raise RuntimeError('Port is used by another app')
        except Exception:raise RuntimeError(f'Cannot open port {a.port}')
        if not a.no_browser:webbrowser.open(f'http://127.0.0.1:{a.port}/')
        return
    if not a.no_browser:threading.Timer(.6,lambda:webbrowser.open(f'http://127.0.0.1:{a.port}/')).start()
    print(f'Fly Piano v4: http://127.0.0.1:{a.port}/',flush=True);server.serve_forever()
if __name__=='__main__':main()
