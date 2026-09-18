import copy,unittest
import numpy as np
from train_sequence import objective,qualify,combine,wilson,population,plateau,new_optimizer,VALIDATION_SEEDS,TEST_SEEDS
from engine import INITIAL,LOW,HIGH

class SequenceTests(unittest.TestCase):
 def test_sparse_precision_cannot_beat_useful_coverage(self):
  sparse=dict(precision=1.,recall=.01,f1=2*.01/1.01)
  useful=dict(precision=.8,recall=.6,f1=2*.8*.6/1.4)
  self.assertGreater(objective(useful),objective(sparse));self.assertFalse(qualify(sparse));self.assertTrue(qualify(useful))
  self.assertFalse(qualify(dict(useful,solver_warnings=1)))
 def test_plateau_transitions_keep_best(self):
  o=new_optimizer(INITIAL.tolist(),55);best=o['best'].copy()
  for _ in range(4):reason=plateau(o,False)
  self.assertEqual(o['mode'],'local');self.assertIsNotNone(reason)
  for _ in range(4):plateau(o,False)
  self.assertEqual(o['mode'],'cem');self.assertEqual(o['restarts'],1);self.assertEqual(o['best'],best)
 def test_resume_population_rng(self):
  o=new_optimizer(INITIAL.tolist(),22);population(o);saved=copy.deepcopy(o)
  np.testing.assert_array_equal(population(o),population(saved))
  o['mode']='local';p=population(o);self.assertTrue(np.all(p>=LOW)&np.all(p<=HIGH))
 def test_pooled_denominators_and_interval(self):
  m=combine([dict(metric=dict(target_notes=100,actual_notes=a,matched=t),warnings=0) for a,t in [(10,8),(100,40)]])
  self.assertAlmostEqual(m['precision'],48/110);self.assertAlmostEqual(m['recall'],48/200)
  lo,hi=wilson(48,110);self.assertLess(lo,m['precision']);self.assertGreater(hi,m['precision'])
 def test_holdout_never_validation(self):self.assertFalse(set(VALIDATION_SEEDS)&set(TEST_SEEDS))
if __name__=='__main__':unittest.main()
