"""Prospective registry. Expected outcomes are hypotheses, never used as data."""
from pathlib import Path
import json

VARIANTS=['full','no_memory','no_cpg','no_feedback','randomized','rnn','hand_cpg','direct','sequence_specific',
          'no_dn','no_intraleg','no_interleg','no_delay','no_inhibition','no_body_mapping']
HYPOTHESES={
'A1':'P1.1/P1.2: tonic DN drive sustains motor rhythm; CPG/DN removal reduces rhythm.',
'A2':'P1.5: changed descending drive changes rhythm after a tempo jump.',
'A3':'P1: removing the symbolic cue leaves endogenous motor rhythm.',
'A4':'P1.4: delayed/noisy/absent feedback increases contact timing error.',
'A5':'P1.3: descending amplitude and lateral bias change global or limb activity.',
'B1':'P2.1/P2.5: an engineered reusable primitive library executes new combinations.',
'B2':'P2.2/P2.4: symbolic task state transfers across keyboard geometry.',
'B3':'P2.3: an engineered allocator recruits an available limb.',
'B4':'P2.1/P2.5: execution extends to held-out motifs and timing patterns.',
'B5':'P2.4: alternative trajectories preserve key-contact success.',
}
def registry(seeds=range(8)):
    design={
      'A1':(['full','no_cpg','no_dn','randomized','no_inhibition','no_delay'],['tonic']),
      'A2':(['full','no_cpg','no_feedback'],['up_small','up_large','down_small','down_large']),
      'A3':(['full','no_cpg','no_feedback'],['interruption']),
      'A4':(['full','no_feedback'],['normal','delayed','noisy']),
      'A5':(['full','no_dn'],['weak','strong','late','left_bias']),
      'B1':(VARIANTS,['novel']),
      'B2':(['full','no_memory','direct','no_body_mapping'],['mirrored','shifted','spacing','height']),
      'B3':(['full','direct','no_memory'],['disable_LF','disable_LM','forced_RF']),
      'B4':(['full','sequence_specific','no_memory'],['long','repeated','nonrepeating','alternating','syncopated']),
      'B5':(['full','direct'],['direct_reach','curved_reach','soft_force']),
    }
    rows=[]
    for exp,(variants,conditions) in design.items():
      for variant in variants:
       for condition in conditions:
        for seed in seeds:
         rid=f'{exp}_{condition}_{variant}_s{seed:02d}'
         rows.append(dict(run_id=rid,experiment_id=exp,hypothesis=HYPOTHESES[exp],variant=variant,
          condition=condition,seed=seed,drive=500.,dt=.002,duration=8.,nkeys=8,input='synthetic symbolic events; tonic only for A1',
          sequence_id=('tonic' if exp=='A1' else f'heldout_{condition}_{seed%3}'),split='test',
          expected_outcome='directional prediction only; null and adverse results retained',
          primary_metrics=['motor_rhythm_power','key_accuracy','timing_mae_s'],
          outputs=[f'data/runs/{rid}/telemetry.npz',f'data/runs/{rid}/metrics.json'],
          interpretation_rule='Support requires paired effect in predicted direction; engineered P2 effects cannot establish learned biological primitives.'))
    return rows
def write_registry(path):
    Path(path).write_text(json.dumps(registry(),indent=2),encoding='utf8')
if __name__=='__main__':write_registry(Path(__file__).with_name('registry.json'))

