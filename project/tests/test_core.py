import sys,unittest,tempfile
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulation.model import MotorNetwork,rewire,ROOT
from body.dynamics import Body
from experiments.run import score_contacts,run
from experiments.registry import registry

class CoreTests(unittest.TestCase):
    def test_graph_degree_preservation(self):
        w=np.load(ROOT/'connectome/weights.npy');r,n=rewire(w,np.random.default_rng(4),2)
        self.assertGreater(n,0)
        np.testing.assert_array_equal((w!=0).sum(0),(r!=0).sum(0));np.testing.assert_array_equal((w!=0).sum(1),(r!=0).sum(1))
        np.testing.assert_allclose(abs(w).sum(1),abs(r).sum(1))
    def test_dn_ablation_blocks_network(self):
        net=MotorNetwork(3,'no_dn')
        for _ in range(1000):net.step(500,-1)
        self.assertEqual(float(net.r.max()),0)
    def test_cpg_ablation_zero(self):
        net=MotorNetwork(3,'no_cpg')
        for _ in range(500):net.step(500,-1)
        self.assertEqual(float(net.r[net.cpg].max()),0)
    def test_ik_forward(self):
        b=Body();b.q[0]=b.ik(0,.2,-.8);self.assertLess(np.linalg.norm(b.points()[1][0]-[.2,-.8]),1e-10)
    def test_contact_requires_geometry(self):
        b=Body();rest=b.q.copy()
        for _ in range(100):b.step(rest,.002)
        self.assertEqual(b.force.max(),0)
        target=b.q.copy();target[0]=b.ik(0,b.x[3],b.height-.05)
        for _ in range(500):b.step(target,.002)
        self.assertGreater(b.force[0],0);self.assertEqual(b.actual[0],3)
    def test_no_duplicate_matches(self):
        events=[dict(event_id=0,key=0,time=1),dict(event_id=1,key=0,time=1.05)]
        m=score_contacts(events,[dict(key=0,time=1.02)])
        self.assertEqual(m['key_accuracy'],.5);self.assertEqual(m['misses'],1)
    def test_wrong_contact_is_not_hit(self):
        m=score_contacts([dict(event_id=0,key=0,time=1)],[dict(key=1,time=1)])
        self.assertEqual(m['key_accuracy'],0);self.assertIsNone(m['timing_mae_s'])
    def test_deterministic_and_finite(self):
        c=registry([19])[0];c.update(duration=.7,run_id='test')
        with tempfile.TemporaryDirectory() as d:
            run(c,d);z=np.load(Path(d)/'test/telemetry.npz');a={k:z[k].copy() for k in z.files};z.close()
            run(c,d);z=np.load(Path(d)/'test/telemetry.npz')
            for k in a:np.testing.assert_array_equal(a[k],z[k]);self.assertTrue(np.isfinite(z[k]).all())
    def test_measured_ids_unique(self):
        n=MotorNetwork();self.assertTrue(n.table.id.is_unique);self.assertEqual(len(n.dn),2);self.assertEqual(len(n.cpg),18)

if __name__=='__main__':unittest.main()
