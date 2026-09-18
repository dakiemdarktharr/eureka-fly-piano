import copy,unittest
import numpy as np
from engine import Engine,INITIAL,match_events
from train_hundred import clip,validate_budget

class HundredTests(unittest.TestCase):
 def test_exact_hundred_retains_duplicate_and_unassigned_targets(self):
  notes=[dict(id=i,start=i//3*.5,end=i//3*.5+2,pitch=60,leg=-1 if i%9==0 else i%6) for i in range(203)]
  before=copy.deepcopy(notes);seen=set()
  for index in [0,100,103]:
   block,d=clip(notes,index);self.assertEqual(len(block),100);seen.update(n['id'] for n in block)
   self.assertGreater(d,max(n['end'] for n in block));self.assertTrue(any(n['leg']==-1 for n in block))
   for n in block:self.assertAlmostEqual(n['end']-n['start'],2)
  self.assertEqual(seen,set(range(203)));self.assertEqual(notes,before)
 def test_100_is_recall_denominator_not_precision_denominator(self):
  target=[dict(id=i,pitch=60,start=float(i),end=i+.2) for i in range(100)]
  actual=[dict(id=i,pitch=60,start=float(i),end=i+.2) for i in range(50)]+[dict(id=50+i,pitch=61,start=float(i),end=i+.2) for i in range(50)]
  m=match_events(target,actual,.1);self.assertEqual(m['matched'],50);self.assertEqual(m['recall'],.5);self.assertEqual(m['precision'],.5)
  actual+= [dict(id=100+i,pitch=61,start=float(i),end=i+.2) for i in range(100)]
  m=match_events(target,actual,.1);self.assertEqual(m['recall'],.5);self.assertEqual(m['precision'],.25)
 def test_repeated_presses_cannot_earn_multiple_matches(self):
  target=[dict(id=0,pitch=60,start=1.,end=1.2)]
  actual=[dict(id=i,pitch=60,start=1.+i*.001,end=1.2) for i in range(10)]
  self.assertEqual(match_events(target,actual,.1)['matched'],1)
 def test_default_skill_has_100_events(self):
  e=Engine();notes,d=e.synthetic(77);self.assertEqual(len(notes),100);self.assertEqual(len({n['id'] for n in notes}),100)
 def test_recorded_trace_is_actual_neural_state(self):
  e=Engine();notes,d=e.synthetic(77,count=2);r,f=e.rollout(INITIAL,notes,d,record=True);off=r['layout']['neuron_rates'][0]
  self.assertEqual(f.shape[1]-off,412);np.testing.assert_array_equal(f[:,off+e.template.dn],f[:,r['layout']['DN'][0]:r['layout']['DN'][0]+2])
  self.assertEqual(r['neuron_ids'],e.template.table.bodyId.astype(str).tolist());self.assertTrue(np.isfinite(f).all())
 def test_budget(self):
  validate_budget(120,4)
  for x in [0,-1,121,float('nan'),float('inf')]:
   with self.assertRaises(ValueError):validate_budget(x,4)

if __name__=='__main__':unittest.main()
