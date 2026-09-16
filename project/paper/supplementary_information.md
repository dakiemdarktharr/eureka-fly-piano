# Supplementary information

This supplement accompanies an exploratory computational feasibility manuscript.
All reported observations come from executed simulations, not literature figures.

S1. `tables/per_run.csv`: all 768 primary runs; one row per registered seed/config.
S2. `tables/summary.csv`: means, medians, SDs, bootstrap CIs, counts and scope.
S3. `tables/contrasts.csv`: paired differences, Cohen dz, raw and Holm p-values.
S4. `tables/extended_metrics.csv`: state dimensionality, inter-leg phase locking,
active limbs, pre/post frequencies, DN/CPG activity and physical contacts.
S5. `tables/representations.csv`: context-dependent task, neural and joint distances.
S6. `../experiments/registry.json`: exact hypotheses, conditions and expected rules.
S7. `../docs/calibration_log.md`: failed pilots and explicit parameter selection.
S8. `../docs/convergence.json`: timestep sensitivity with fixed physical delay.
S9. `../connectome_manifest.json`: source snapshots, filters, IDs and checksums.
S10. `../docs/internal_review.md`: three-perspective critical internal review.

The raw telemetry arrays are time, rates, task, q, dq, torque, force, actual,
target, limb, key_x, key_height and hips. Rates and body state are stored at every
2 ms sample. `metadata.json` provides events, physical contact records, controller
identity, seed, source revision and config/graph/telemetry checksums.

All mechanical quantities are nondimensional. Rate states are not spike recordings.
Missing timing metrics denote absent successful matches, never perfect performance.

# Methods appendix

The executable definition is `simulation/model.py` and `body/dynamics.py`; the model
configuration is descriptive and the experiment registry supplies each run's inputs.
All neural states begin at zero. Python NumPy PCG64 seeds 0-7 define evaluation
parameter draws; 100 and 101 are engineering calibration seeds. A separate seed offset
5000 generates noisy sensory input, and 9100 plus seed modulo 3 generates symbolic
test sequences. The three sequence identities repeat across seeds; seeds are not
eight independent songs. There is one measured anatomical connectome instance.

For each neuron, the rate ODE is:

`dr_i/dt = (-r_i + max(0, cap_i*tanh(gain_i*(I_i + 0.03*sum_j W_ji*r_j - threshold_i)/cap_i))) / tau_i`.

W is the measured signed count matrix, with pre/post orientation tested during
extraction. Volume normalization uses the median of the entire released table,
not the median of the selected 412 cells. Parameters are normally distributed and
clipped below small positive bounds; this is not exactly a truncated-normal draw.
Numerical integration is forward Euler. Synaptic buffers delay rate coupling by
two update steps (4 ms at the core 2 ms step); the zero-delay ablation removes the
buffer. This is an assumption, not an inferred synaptic latency. The source preprint
used a different integration method; we do not claim a numerical reproduction.

The synthetic symbolic relay is outside the measured connectome. Eight leaky units
receive the target key; the decoder reads the largest relay value above 0.2. The
sequencer reveals each key 0.2 s before its target time and gates a 0.13 s press.
This timing information is an explicit privileged input. It is appropriate to the
controlled symbolic mode but invalid as evidence of inferred tempo or musical
understanding. The task relay contributes eight additional synthetic state variables.

The leg allocator minimizes distance in joint-angle space and excludes disabled
limbs. Inverse kinematics maps the selected key position to a two-joint target;
equal-weight MN population activity gates the downward press depth. The task target
therefore bypasses measured neural layers for spatial and temporal specification.
This shortcut is intentional in this feasibility version and prevents attribution
of compositional behavior to the connectome. The MN path still gates contact force.

The primitive library is hand-coded reach/press/release and hold scheduling, not a
learned memory. `no_memory` removes anticipatory reaching while retaining the same
allocator and geometry. It is a reach-primitive lesion, not synaptic-plasticity
ablation. `sequence_specific` uses a fixed key order; `direct` uses key modulo six
and the original layout; `hand_cpg` supplies analytic 8 Hz sinusoidal readout drive.
The state-size-matched RNN is a fixed random reservoir with 412 rate states and is
untrained; it is not a fair comparison to an optimized recurrent controller.
CPG/direct baselines also record the anatomical model as a shadow telemetry stream;
their body drive comes from their named alternative controller. Displays must not
imply the shadow stream caused baseline body movements.

Joint dynamics use inertia 0.08, a torque-limited PD servo (32, 1.4), intrinsic
damping 0.25, and a unilateral keyboard spring/damper (180, 1.5). Contact force is
mapped into generalized joint torque through the analytic foot-height Jacobian.
Contacts are detected from geometry and force, never inserted from target events.
There is no mass-calibrated fly body, muscle model, floor reaction, or free walking.
Units are nondimensional, so energy is an effort proxy rather than joules.

Key accuracy uses one-to-one same-key contact matching within +/-0.25 s. This is a
broad tolerance chosen for the surrogate; timing MAE is conditional on matched hits.
Failures have missing timing values, not zero error. Extra contacts and precision
must be considered alongside recall. The rhythmicity measure is spectral peak
power / total spectral power over the last half of the trial, for variable active
MNs (variance >0.1 and max rate >1 Hz), with candidate peaks restricted to 1-40 Hz.
It is not the autocorrelation measure used by the source preprint and does not by
itself establish a limit cycle. Participation ratio uses covariance trace identities;
phase locking uses analytic phases only for varying leg-population traces.

Summary CIs bootstrap seed-level run values with 4,000 resamples, fixed analysis
seed 9901. Paired t-tests and paired Cohen dz compare matched seeds, with Holm
correction across all generated primary contrasts. Zero-variance nonzero contrasts
receive undefined p-values/effect sizes, not artificial significance. Sample sizes
are small, parameter replicates are not biological replicates, and sequence-level
uncertainty is not estimated independently. All results are exploratory.

Geometry is downloaded from pinned malevnc R data. Native vertices are in microns.
Region colors average cells by somaNeuromere and do not assert their full arbor lies
in that region. Single-neuron structural diagrams use schematic positions. No
registered FlyWire-to-MANC brain/VNC bridge or neuron-specific mesh is provided.
