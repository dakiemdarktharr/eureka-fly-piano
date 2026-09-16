# Internal review through three disciplinary perspectives

This is a critical self-review by the implementing assistant, not three independent
human reviews or three independently executed agent assessments.

## Computational neuroscience perspective

**Major revision / no-go for the original biological claims.** The measured subgraph
is real and retains source neuron IDs and signed counts. Its rhythm-generating
capacity and loss under CPG/DN lesions are supported by executed trials. However,
there is no reconstructed brain population, no measured sensory projection, no
physiologically validated gain/delay distribution, no exact neuron arbor mapping,
and no animal validation. One male connectome cannot estimate between-fly variation.
The body-readout mapping ignores muscle identity and the true excitatory action of
neuromuscular transmission; CNS glutamate signs must not be transferred to muscles.

The core CPG hypothesis is prior work, currently a preprint in the consulted record.
The project must not rebrand that discovery as novel. A1 illustrates the implemented
motif's dynamics, not a new CPG discovery. A2 is drive modulation, not a validated
tempo-state command. A4's null result does not falsify biological proprioception.
Seven retained inter-leg edges and missing premotor/sensory circuitry make global
coordination conclusions premature. No spike timing is available in this rate model.

## Machine learning and robotics perspective

**No-go for learned compositional-generalization claims.** The task relay and decoder
receive exact key and timing information, and no trainable model is fitted. Thus
task-state invariance is imposed, not discovered. The no_memory label denotes
removal of anticipatory reaching, not a learned memory or plasticity ablation.
The RNN is state-size-matched but untrained, and the sequence-specific controller
is a deliberately simple fixed order. These are shortcut diagnostics, not fair
training/sample-efficiency baselines.

The simple task exposes the shortcut: randomized connectivity and the random
reservoir obtain perfect recall without qualifying motor rhythm. Full-network
performance is weaker. There is no evidence that a connectome supplies the sequence
computation. Body interaction is genuinely integrated torque/contact dynamics, but
only in a tethered two-link-per-leg surrogate with uncalibrated physical units.
Nearest-leg allocation may switch limbs during a reach; this is an architectural
limitation retained in the evaluated protocol, not concealed as biological control.

## Reproducibility editor perspective

The executable registry, all-seed telemetry, checksums, source snapshots, dependency
lock and scripts are strengths. Initial Windows file-handle cleanup and viewer-path
bugs were fixed. Variant-specific replay graphs now follow actual rewiring/lesions;
shadow activity for direct/hand-CPG baselines is explicitly labeled. Missing NT
confidence is shown as unknown. Raw contacts, including misses and extras, are retained.

The clean-checkout audit must be read for the actual tested environment. Cross-OS,
Docker and GPU equivalence are not inferred. Video byte identity is not guaranteed
across ffmpeg/font versions; numerical telemetry is the primary comparison target.
The source graph's upstream neuPrint release remains unspecified by the export,
and public redistribution rights need resolution. There is no public repository,
Zenodo DOI, finalized authorship or authorized song media. Local tagging alone is
not a publication-ready release. Authorship and data/code availability statements
must remain candid.

## Timestamp and attribution audit

Each recorded step labels the input/contact evaluation time t. The rate and joint
arrays contain the just-updated state (nominally t + dt), while force and key-contact
observations are computed before the body update. This within-step staggering is
2 ms in the main batch and is preserved in replays. It must not be interpreted as
sub-millisecond synchrony. Continuous-time contact interpolation was not performed.
The responsible-MN field means the most active member of a population readout at
that step, not a proven unique causal cell. Structural paths are not causal paths.

## Corrected before handoff

- Streamed the dense source in its true column-major ordering, with sign checks.
- Retained all failed calibration outcomes in the calibration log.
- Replaced ambiguous spike labeling with modeled rate labeling.
- Fixed variant-specific edges and synthetic RNN identity in replay.
- Fixed the browser's root script path and verified the replay controls.
- Fixed open-file cleanup on Windows and preserved undefined metrics as missing.
- Added fixed-physical-delay timestep sensitivity and explicit source licensing gates.

## Remaining research requirements

A measured brain/descending bridge; richer premotor/sensory circuitry; identified
muscle readout; validated body; learned and capacity-matched primitive/RNN controls;
independent sequence and connectome holdouts; prospective adaptation/recovery metrics;
exact neuronal meshes; authorized song media; public archive and DOI. These are
substantive missing parts, so the original A-to-Z mission is not complete.
