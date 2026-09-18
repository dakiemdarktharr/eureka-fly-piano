import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from train import passes
from engine import partition,LOW,HIGH,INITIAL
from paths import atomic_json,read_json
import tempfile

class ProtocolTests(unittest.TestCase):
 def result(self,p=.86,r=.86,f=.86):return {k:dict(precision=p,recall=r,f1=f,target_notes=100,actual_notes=100,solver_warnings=0) for k in ['merry','pool']}
 def test_precision_only_is_insufficient(self):self.assertFalse(passes(self.result(1,.01,.02)))
 def test_both_songs_must_pass(self):
  x=self.result();x['pool']['precision']=.84;self.assertFalse(passes(x))
 def test_strict_precision_boundary(self):self.assertFalse(passes(self.result(.85)));self.assertTrue(passes(self.result(.85001)))
 def test_empty_or_divergent_rollout_fails(self):
  for field,value in [('target_notes',0),('actual_notes',0),('solver_warnings',1)]:
   x=self.result();x['merry'][field]=value;self.assertFalse(passes(x))
 def test_split_has_gaps(self):
  s={'bars':[{'start':i*3,'end':(i+1)*3} for i in range(100)],'duration':300};p=partition(s)
  self.assertLess(p['train'][1],p['validation'][0]);self.assertLess(p['validation'][1],p['test'][0]);self.assertEqual(p['test'][1],300)
 def test_policy_bounds(self):self.assertEqual(len(INITIAL),16);self.assertTrue((INITIAL>=LOW).all() and (INITIAL<=HIGH).all())
 def test_atomic_state_roundtrip(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'state.json';atomic_json(p,{'state':'paused','value':'tiếng Việt'});self.assertEqual(read_json(p)['value'],'tiếng Việt');self.assertEqual(len(list(Path(d).iterdir())),1)
if __name__=='__main__':unittest.main()
