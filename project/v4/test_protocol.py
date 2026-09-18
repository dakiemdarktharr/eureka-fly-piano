import unittest,copy
from v4_paths import PROJECT
HAS_DATA=(PROJECT/'connectome/weights.npy').exists()
import numpy as np
from engine import Engine,Detector,INITIAL,LOW,HIGH,match_events
from train import skill_pass,sequence_pass

class ProtocolTests(unittest.TestCase):
    def test_no_precision_only_success(self):
        self.assertFalse(skill_pass({'precision':1,'recall':.1}))
        self.assertFalse(sequence_pass({'precision':1,'recall':.1,'f1':.18}))
        self.assertFalse(sequence_pass({'precision':.85,'recall':1,'f1':.9}))
    def test_one_to_one_no_reward_farming(self):
        target=[dict(id=0,pitch=60,start=1.,end=1.2)]
        actual=[dict(id=i,pitch=60,start=1.+i*.001,end=1.1) for i in range(10)]
        m=match_events(target,actual)
        self.assertEqual(m['matched'],1);self.assertEqual(m['extra'],9)
    def test_debounce_release(self):
        d=Detector();f=np.zeros(88);f[39]=.01
        for j in range(100):d.step(f,j*.002)
        self.assertEqual(len(d.events),1)
        for j in range(100,120):d.step(np.zeros(88),j*.002)
        self.assertIsNotNone(d.events[0]['end'])
    @unittest.skipUnless(HAS_DATA,'Private model inputs are not in the repository')
    def test_exact_batch_parity(self):
        e=Engine();n,t=e.synthetic(5,count=2)
        a=e.rollout(INITIAL,n,t,batched=False);b=e.rollout(INITIAL,n,t)
        np.testing.assert_array_equal(a['final_qpos'],b['final_qpos'])
        self.assertEqual(a['actual'],b['actual']);self.assertEqual(a['physics_steps'],round(t/.002)*10)
        self.assertEqual(e.w.model.opt.noslip_iterations,5)
    @unittest.skipUnless(HAS_DATA,'Private model inputs are not in the repository')
    def test_synaptic_structure_and_sign(self):
        e=Engine();a=e.template.w.copy();b=a.copy();scale=np.exp(np.linspace(-.69,.69,24)[e.group]);scale[e.template.dn]=1
        b.data*=np.repeat(scale,np.diff(b.indptr))
        np.testing.assert_array_equal(a.indices,b.indices);np.testing.assert_array_equal(np.sign(a.data),np.sign(b.data))
        self.assertGreater(np.linalg.norm(b.data-a.data),0)
    @unittest.skipUnless(HAS_DATA,'Private model inputs are not in the repository')
    def test_invalid_parameters(self):
        e=Engine();n,t=e.synthetic(1,count=1)
        with self.assertRaises(ValueError):e.rollout(HIGH+1,n,t)

if __name__=='__main__':unittest.main()
