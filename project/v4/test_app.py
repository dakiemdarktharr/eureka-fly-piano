"""HTTP tests use isolated state and never start a learning worker."""
import tempfile,threading,unittest,json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
import app
from unittest.mock import patch
class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();app.STATE=Path(cls.temp.name)
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_address[1]}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.temp.cleanup()
    def call(self,path,headers=None,data=None):
        req=Request(self.base+path,headers=headers or {},data=None if data is None else json.dumps(data).encode())
        try:
            with urlopen(req,timeout=3) as r:return r.status,r.read()
        except HTTPError as e:return e.code,e.read()
    def test_health(self):
        code,body=self.call('/api/health');self.assertEqual(code,200);self.assertEqual(json.loads(body)['version'],4)
    def test_foreign_host_cannot_read_token(self):
        code,_=self.call('/api/state',{'Host':'external.example'});self.assertEqual(code,403)
    def test_job_requires_token(self):
        code,_=self.call('/api/train',data={'minutes':1});self.assertEqual(code,403)
    def test_origin_guard(self):
        code,_=self.call('/api/train',{'Origin':'https://external.example','X-FlyPiano-Token':app.TOKEN},{});self.assertEqual(code,403)
    def test_invalid_budget_never_launches_worker(self):
        code,_=self.call('/api/train',{'X-FlyPiano-Token':app.TOKEN},{'minutes':0});self.assertEqual(code,400);self.assertIsNone(app.CHILD)
    def test_two_hour_budget_can_launch(self):
        with patch.object(app,"readiness",return_value={"ready":True}), patch.object(app,"launch") as launch:
            code,_=self.call("/api/train",{"X-FlyPiano-Token":app.TOKEN},{"minutes":120,"workers":4})
            self.assertEqual(code,200);launch.assert_called_once_with(120.,4)

    def test_over_two_hour_budget_rejected(self):
        with patch.object(app,"readiness",return_value={"ready":True}), patch.object(app,"launch") as launch:
            code,_=self.call("/api/train",{"X-FlyPiano-Token":app.TOKEN},{"minutes":121,"workers":4})
            self.assertEqual(code,400);launch.assert_not_called()

    def test_file_allowlist(self):
        code,_=self.call('/v4/train.py');self.assertEqual(code,404)
if __name__=='__main__':unittest.main()
