# Calibration and protocol history

Before the benchmark batch, a pilot using descending input 250 yielded no sustained
motor activity (seed 0). This is preserved as a reported failure, not an excluded
benchmark seed. The graph's full-VNC median volume is 480,536,186 native volume units.
Because size normalization affects thresholds, a three-point input calibration was
performed with seed 100, which is excluded from evaluation:

| Drive | MN spectral concentration | Mean oscillatory MN frequency |
|---|---:|---:|
| 250 | 0 | undefined |
| 500 | 0.74186 | 8.96154 Hz |
| 1000 | 0.73997 | 9.27660 Hz |

The smallest tested drive with sustained activity (500) was frozen before the full
eight-seed benchmark. This is a calibration, not a reproduction of the source paper's
full simulation: the retained subgraph and normalization population differ.

An initial decoder averaged activity across all MNs, dividing by 40 Hz; most MNs were
silent, and no contacts occurred. It was replaced with an explicit equal-weight sum
of leg MN rates divided by 40 Hz. Separate seed 101 body calibration produced key
accuracy 0.5833 for full, 0.8333 for direct, 1.0 for hand CPG, and 0.5 for no CPG.
Those calibration outcomes are not counted in benchmark confidence intervals.
The body and readout are engineering choices, and contact success cannot be
attributed exclusively to neural rhythmicity.

Evaluation seeds: 0-7. No model optimization is performed during these trials.
Registry hypotheses preceded the batch but followed engineering calibration; this
is not an independently registered or blinded confirmatory experiment.
