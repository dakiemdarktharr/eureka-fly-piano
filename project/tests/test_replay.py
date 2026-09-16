import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from visualization.replay import replay
from simulation.model import ROOT

class ReplayChecks(unittest.TestCase):
    @unittest.skipUnless((ROOT/'data/runs/B1_novel_no_cpg_s00/metadata.json').exists(),'requires benchmark telemetry')
    def test_ablated_edges_not_drawn(self):
        r=replay('B1_novel_no_cpg_s00',fps=2)
        self.assertTrue(all(not n['downstream'] for n in r['neurons'] if n['kind']=='CPG'))
    @unittest.skipUnless((ROOT/'data/runs/B1_novel_rnn_s00/metadata.json').exists(),'requires benchmark telemetry')
    def test_rnn_has_no_anatomical_identity(self):
        r=replay('B1_novel_rnn_s00',fps=2)
        self.assertTrue(all(n['id'].startswith('rnn_slot_') and n['region']=='not anatomical' for n in r['neurons']))
    @unittest.skipUnless((ROOT/'data/runs/B1_novel_full_s00/metadata.json').exists(),'requires benchmark telemetry')
    def test_fixed_scales_and_indices(self):
        r=replay('B1_novel_full_s00',fps=25)
        self.assertEqual(r['legend']['neuron_rate_hz'],[0,250])
        self.assertEqual(r['frames']['raw_index'][1],20)
        self.assertAlmostEqual(r['frames']['time'][1],.04)

if __name__=='__main__':unittest.main()
