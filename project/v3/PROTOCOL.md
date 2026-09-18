# Protocol v3 - checkpointed motor-controller learning

Frozen initial design, 2026-09-18; retain all unsuccessful runs.

The learned object is a 16-parameter score-conditioned motor readout, optimized
by cross-entropy policy search (CEM). The 412-neuron connectome, physics, score,
contact detector and matching rule are frozen. This is genuine optimization
from physical rollouts, not replay renamed as training, and not synaptic
learning in an animal. The score-to-IK privileged information remains explicit.

Two song timelines are partitioned chronologically into approximately 60% train,
20% validation and 20% test, by whole bars with a one-bar gap at boundaries.
This is within-piece holdout, not unseen-composition generalization; repeated
motifs may occur across partitions. Random six-second clips from train regions
drive CEM. Fixed train-monitor and validation clips provide comparable curves.
The test partition is evaluated once per completed budget campaign, after
checkpoint selection; repeating/resuming campaigns consumes the test holdout.

Default checkpoints: before learning and at 1, 5 and 15 cumulative minutes of
optimizer interaction time. Actual times can overshoot to finish an evaluation.
Also log end-to-end wall time, physics steps, candidates, seed and parameters.
Validation/checkpoint overhead is counted separately, not mislabeled as learning.

Success requires precision > 0.85 AND recall >= 0.85 AND F1 >= 0.85 on BOTH
validation song subsets at three consecutive scheduled checkpoints. This is an
operational gate, not a statistical confidence guarantee. Zero predictions fail.
The default 15-minute optimizer budget saves resumable state if unmet; it does
not convert failure into success. Final held-out test must be reported separately.

Do not optimize thresholds, hide false positives, remove difficult target notes,
alter the keyboard or quote in-sample precision as a test result. No guarantee
that 85% is attainable under these anatomical/actuator/OMR constraints.

Full-song replay of the selected checkpoint is a demonstration combining seen
and held-out material, clearly separated from validation and test statistics.
Whole-body numerical convergence and biology remain open, as in v2.
