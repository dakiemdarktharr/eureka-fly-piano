"""Local research app with protected job controls and an isolated worker."""
import argparse,json,os,re,secrets,subprocess,sys,threading,webbrowser
from pathlib import Path
from urllib.parse import urlsplit,unquote
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from paths import PROJECT,V2,V3,STATE,RUNS,FROZEN,read_json,atomic_json,readiness

if FROZEN:
 STATE.mkdir(parents=True,exist_ok=True)
 if sys.stdout is None:sys.stdout=(STATE/'app.log').open('a',encoding='utf8',buffering=1)
 if sys.stderr is None:sys.stderr=sys.stdout

TOKEN=secrets.token_urlsafe(32);LOCK=threading.Lock();CHILDREN={}
ACTIVE={'queued','training','evaluating','testing','exporting'}
ID=re.compile(r'^[0-9]{8}T[0-9]{6}-s[0-9]+-[0-9a-f]{4}$')
def run_folder(run_id):
 if not isinstance(run_id,str) or not ID.fullmatch(run_id):raise ValueError('Invalid run id')
 folder=RUNS/run_id
 if not (folder/'config.json').is_file():raise ValueError('Run not found')
 return folder
def alive(pid):
 try:
  import psutil
  return bool(pid) and psutil.pid_exists(int(pid))
 except (ValueError,TypeError):return False
def all_runs():
 result=[]
 for p in sorted(RUNS.glob('*/status.json'),reverse=True):
  try:
   s=read_json(p)
   if s.get('state') in ACTIVE and s.get('pid') and not alive(s['pid']):s['state']='interrupted';s['message']='Worker không còn chạy; có thể tiếp tục từ checkpoint'
   if (p.parent/'test_history.json').exists():s['test_history']=read_json(p.parent/'test_history.json')
   result.append(s)
  except (OSError,ValueError):continue
 return result
def busy():return any(s['state'] in ACTIVE for s in all_runs())
def launch(run_id,action='train',minutes=None):
 folder=run_folder(run_id)
 command=[sys.executable,'--worker',run_id] if FROZEN else [sys.executable,str(V3/'app.py'),'--worker',run_id]
 command+=['--action',action]
 if minutes is not None:command+=['--minutes',str(minutes)]
 log=(folder/'worker.log').open('ab')
 try:p=subprocess.Popen(command,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
 finally:log.close()
 CHILDREN[run_id]=p
 s=read_json(folder/'status.json');s.update(state='exporting' if action=='export' else 'queued',pid=p.pid);atomic_json(folder/'status.json',s)

class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kw):super().__init__(*args,directory=str(PROJECT),**kw)
 def log_message(self,fmt,*args):pass
 def json(self,value,status=200):
  data=json.dumps(value,ensure_ascii=False,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def end_headers(self):
  self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store');super().end_headers()
 def list_directory(self,path):self.send_error(404)
 def route(self,path):
  if path=='/':return V3/'ui/index.html'
  if path in ['/dashboard.js','/dashboard.css','/manifest.webmanifest','/icon.svg']:return V3/'ui'/path[1:]
  if path in ['/viewer','/viewer/']:return V3/'ui/viewer/index.html'
  if path.startswith('/ui/vendor/'):return V2/path.lstrip('/')
  if path in ['/ui/app.js','/ui/style.css']:return V3/'ui/viewer'/Path(path).name
  if path in ['/assets/scene.json','/assets/brain.json','/assets/attribution.json']:return V2/path.lstrip('/')
  if re.fullmatch(r'/data/(merry|pool)_(full|constant|score|reference)\.(json|bin|mid)',path):return V2/path[1:]
  if re.fullmatch(r'/data/(merry|pool)_trained\.(json|bin)',path):
   active=STATE/'active_replay.json'
   if not active.exists():return None
   rid=read_json(active)['run_id'];return run_folder(rid)/'replays'/Path(path).name
  if re.fullmatch(r'/scores/private/song[12]_[a-z0-9_\-]+\.pdf',path):return V2/path[1:]
  if path=='/paper/manuscript.pdf':return V3/'output/pdf/manuscript_v3_vi.pdf'
  if path=='/paper/reviewer.pdf':return V3/'output/pdf/reviewer_v3_vi.pdf'
  return None
 def do_GET(self):
  path=unquote(urlsplit(self.path).path)
  if path=='/api/health':return self.json({'ok':True,**readiness()})
  if path=='/api/state':return self.json({'csrf':TOKEN,'readiness':readiness(),'runs':all_runs(),'active_replay':read_json(STATE/'active_replay.json') if (STATE/'active_replay.json').exists() else None})
  if path=='/api/export':
   from urllib.parse import parse_qs
   try:folder=run_folder(parse_qs(urlsplit(self.path).query).get('run',[''])[0]);return self.json({'config':read_json(folder/'config.json'),'status':read_json(folder/'status.json'),'test_history':read_json(folder/'test_history.json') if (folder/'test_history.json').exists() else []})
   except (ValueError,OSError) as e:return self.json({'error':str(e)},404)
  try:file=self.route(path)
  except (ValueError,OSError):return self.send_error(404)
  if file is None or not file.is_file():return self.send_error(404)
  self._file=file
  return super().do_GET()
 def translate_path(self,path):return str(getattr(self,'_file',V3/'missing'))
 def do_POST(self):
  origin=self.headers.get('Origin');host=self.headers.get('Host','')
  if origin and origin not in [f'http://{host}',f'https://{host}']:return self.json({'error':'Origin rejected'},403)
  if not secrets.compare_digest(self.headers.get('X-FlyPiano-Token',''),TOKEN):return self.json({'error':'Invalid request token'},403)
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<4096:raise ValueError('Invalid request length')
   data=json.loads(self.rfile.read(length));path=urlsplit(self.path).path
   with LOCK:
    if path=='/api/train':
     if busy():return self.json({'error':'Một worker đang chạy; hãy tạm dừng hoặc chờ hoàn tất'},409)
     if not readiness()['ready']:return self.json({'error':'Thiếu dữ liệu đầu vào','missing':readiness()['missing']},409)
     from train import create_run
     minutes=float(data.get('minutes',15));seed=int(data.get('seed',0))
     if not 0<=seed<=100000:raise ValueError('Invalid seed')
     rid=create_run(minutes,seed);launch(rid);return self.json({'run_id':rid},201)
    if path in ['/api/pause','/api/resume','/api/replay']:
     rid=data.get('run_id');folder=run_folder(rid)
     if path=='/api/pause':(folder/'pause.request').write_text('pause',encoding='utf8');return self.json({'run_id':rid,'state':'pause_requested'})
     if busy():return self.json({'error':'Một worker đang chạy'},409)
     if not (folder/'optimizer.json').exists():raise ValueError('No optimizer checkpoint available')
     if path=='/api/replay':launch(rid,'export');return self.json({'run_id':rid,'state':'exporting'})
     minutes=float(data.get('minutes',15))
     if not 1<=minutes<=1440:raise ValueError('Budget outside 1–1440 minutes')
     launch(rid,'resume',minutes);return self.json({'run_id':rid,'state':'resuming'})
    return self.json({'error':'Unknown action'},404)
  except (ValueError,TypeError,KeyError,OSError) as e:return self.json({'error':str(e)},400)

def main():
 p=argparse.ArgumentParser();p.add_argument('--worker');p.add_argument('--action',choices=['train','resume','export'],default='train');p.add_argument('--minutes',type=float);p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=8877);p.add_argument('--no-browser',action='store_true');args=p.parse_args()
 STATE.mkdir(parents=True,exist_ok=True);RUNS.mkdir(exist_ok=True)
 if args.worker:
  from train import train,export_replays
  if args.action=='export':
   folder=run_folder(args.worker);previous=read_json(folder/'status.json')
   try:export_replays(args.worker);previous.update(state='target_met' if previous.get('target_met') else 'budget_exhausted',message='Đã xuất replay toàn bài từ checkpoint đã học');atomic_json(folder/'status.json',previous)
   except Exception as e:previous.update(state='failed',message=str(e));atomic_json(folder/'status.json',previous);raise
  else:train(args.worker,args.minutes if args.action=='resume' else None)
  return
 try:server=ThreadingHTTPServer((args.host,args.port),Handler)
 except OSError:
  if not args.no_browser:webbrowser.open(f'http://127.0.0.1:{args.port}/')
  return
 if not args.no_browser:threading.Timer(.4,lambda:webbrowser.open(f'http://127.0.0.1:{args.port}/')).start()
 server.serve_forever()

if __name__=='__main__':
 try:main()
 except Exception:
  import traceback
  traceback.print_exc()
  sys.exit(1)
