"""Loopback-only replay server. Explicit run requests are restricted to registry IDs."""
from pathlib import Path
import sys,json,urllib.parse,threading
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from visualization.replay import replay
from simulation.model import ROOT
from experiments.registry import registry
from experiments.run import run

LOCK=threading.Lock();CONFIGS={c['run_id']:c for c in registry()}
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def json(self,obj,status=200):
        data=json.dumps(obj,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        u=urllib.parse.urlparse(self.path)
        if u.path=='/api/runs':return self.json([{'id':k,'available':(ROOT/'data/runs'/k/'metrics.json').exists()} for k in CONFIGS])
        if u.path=='/api/replay':
            rid=urllib.parse.parse_qs(u.query).get('id',[''])[0]
            if rid not in CONFIGS:return self.json({'error':'unknown run'},404)
            try:return self.json(replay(rid))
            except (OSError,ValueError) as e:return self.json({'error':str(e)},404)
        if u.path=='/':self.path='/app/index.html'
        return super().do_GET()
    def do_POST(self):
        if self.path!='/api/run':return self.json({'error':'unsupported'},404)
        # Same-origin requests only. No arbitrary paths, commands or parameters.
        origin=self.headers.get('Origin','')
        if origin and origin not in [f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}']:return self.json({'error':'origin rejected'},403)
        try:
            length=int(self.headers.get('Content-Length',0))
            if not 0<length<500:raise ValueError('invalid request length')
            rid=json.loads(self.rfile.read(length))['id']
            if rid not in CONFIGS:raise ValueError('unknown run')
            if not LOCK.acquire(blocking=False):return self.json({'error':'experiment already running'},409)
            try:run(CONFIGS[rid])
            finally:LOCK.release()
            return self.json({'id':rid,'status':'complete'})
        except (ValueError,KeyError) as e:return self.json({'error':str(e)},400)
if __name__=='__main__':
    port=int(sys.argv[1]) if len(sys.argv)>1 else 8765
    print(f'Open http://127.0.0.1:{port}',flush=True);ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
