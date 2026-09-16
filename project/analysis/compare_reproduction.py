"""Compare fresh-checkout core outputs with the original registered observations."""
from pathlib import Path
import argparse, json, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from connectome.prepare import sha, dump

def compare(checkout):
    other = Path(checkout).resolve() / 'project'
    result = {'status': 'pass', 'comparison': 'exact array equality on the same Windows host',
              'checkout': str(other.parent), 'runs': [], 'source_checksums': {}}
    for name in ['weights.npy', 'neurons.csv', 'anatomy.json']:
        same = sha(ROOT/'connectome'/name) == sha(other/'connectome'/name)
        result['source_checksums'][name] = same
        assert same, name
    for rid in ['A1_tonic_full_s00', 'A1_tonic_no_cpg_s00', 'A1_tonic_no_dn_s00', 'B1_novel_full_s00']:
        a, b = ROOT/'data/runs'/rid, other/'data/core/runs'/rid
        with np.load(a/'telemetry.npz') as x, np.load(b/'telemetry.npz') as y:
            assert x.files == y.files
            equal = {k: bool(np.array_equal(x[k], y[k], equal_nan=True)) for k in x.files}
        assert all(equal.values()), (rid, equal)
        ma, mb = json.loads((a/'metrics.json').read_text()), json.loads((b/'metrics.json').read_text())
        ma.pop('wall_seconds', None); mb.pop('wall_seconds', None)
        assert ma == mb, rid
        result['runs'].append({'run_id': rid, 'arrays_equal': equal, 'scientific_metrics_equal': True, 'excluded_metric': 'wall_seconds',
                               'telemetry_sha256': sha(b/'telemetry.npz')})
    dump(ROOT/'docs/reproduction_comparison.json', result)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('checkout'); args=parser.parse_args()
    compare(args.checkout)
