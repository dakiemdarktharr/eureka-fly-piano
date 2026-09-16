# A connectome-derived VNC benchmark exposes the separation between rhythmic dynamics and engineered key execution

Computational feasibility manuscript | 17 September 2026 | Version 0.1.0

Authorship and affiliations: to be supplied by the project owner. This report is not submission-ready. It reports executed computational results, including negative findings; it does not claim completion of the original brain-piano research program.

## Abstract

Can measured fly motor connectivity support rhythmic dynamics, and does that structure confer reusable task-level motor control? We constructed an auditable feasibility benchmark using a 412-neuron subgraph of the male adult nerve cord (MANC): two descending neurons, 18 candidate central pattern generator (CPG) interneurons, and 392 leg motor neurons. A rate model drove a tethered six-leg, two-joint-per-leg dynamical surrogate through an explicitly engineered symbolic relay and body decoder. Across 768 registered runs, 15 model/controller variants and eight parameter seeds, tonic input yielded motor spectral concentration 0.729 (SD 0.082; 95% bootstrap CI 0.671-0.776). CPG, descending-neuron, inhibitory-edge and randomized-connectivity conditions had no qualifying sustained motor rhythm in A1. However, novel-sequence key accuracy was only 0.531 (SD 0.209; 95% bootstrap CI 0.385-0.646). A hand-coded CPG, randomized graph and fixed untrained reservoir each achieved perfect contact recall on this simple symbolic task. Removing anticipatory reaching did not degrade contact recall as predicted. These results support a restricted computational rhythm-generation finding, but do not support learned compositional control or a connectome advantage for piano execution. Privileged target timing and an engineered spatial decoder explain why strong task performance can coexist with absent neural rhythmicity. The framework provides raw telemetry, causal interventions, conservative statistical summaries, anatomical-region visualization and synchronized replay, while identifying the biological and reproducibility requirements that remain unresolved.

## Introduction

Connectomes constrain which neurons can interact but do not uniquely specify neural dynamics or behavior. A convincing embodied model must distinguish functions attributable to measured wiring from functions supplied by its input encoding, readout and body controller. An artificial keyboard provides discrete contact goals and timing errors that make this distinction observable. It is not evidence that a real fly represents music, naturally plays an instrument, or learns the semantic meaning of a melody.

The adult brain reconstruction establishes a detailed anatomical resource [Dorkenwald2024]. Brain-scale computational modeling has generated experimentally testable sensorimotor predictions [Shiu2024]. Neither precedent removes the need to test the specific neural-to-body mapping used by a new motor benchmark. We therefore ask two narrowly framed questions about hierarchical rhythmic control and reusable task primitives, and report where our implementation does not operationalize them sufficiently.

## Related Work

The female VNC reconstruction and motor-neuron atlas provide an important anatomical reference distinct from our male VNC source [Azevedo2024]. Descending-to-motor circuit organization in MANC provides a foundation for selecting motor pathways [Cheong2026]. The consulted eLife page is the July 2026 Version of Record; treating it simply as the earlier preprint would be inaccurate.

Our core-cell selection and rate-equation assumptions are informed by a walking-CPG study [Pugliese2026]. The consulted PubMed record identifies the April 2026 revision as a preprint, not a journal-reviewed article. Its reported cellular circuit and model results motivated this implementation; our reduced graph, Euler integration, feedback and body decoder are different and are not claimed to reproduce that study's full analysis.

NeuroMechFly v2 demonstrates a richer embodied sensorimotor modeling environment [WangChen2024]. We did not implement its biomechanical body. Recent whole-brain graph-policy work trains connectome-structured controllers through imitation learning and reinforcement learning for locomotion [FlyGM2026]. That prior art prevents a general novelty claim for connecting a fly connectome to a virtual body. A fresh search also identified adjacent larval excitatory-inhibitory motif work [Larval2026], but only its abstract was verified, so it supplies no quantitative premise here. This manuscript makes no priority claim.

## Research Questions and Hypotheses

Principle 1 is hierarchical rhythmic motor control: descending input modulates a low-dimensional motor state, local VNC circuits generate rhythmic activity, and body feedback stabilizes execution. We tested tonic drive, CPG/DN lesions, inhibitory and delay interventions, input-amplitude changes, cue interruption and feedback perturbations. These are model interventions, not animal experiments.

Principle 2 is motor-primitive reuse and task-space invariance: task-level goals should be composable and remappable across body and layout contexts. The desired biological claim requires learned or independently established task-level primitives and a constrained neural implementation. Our implementation only provides an engineered reach/press/release library and allocator. Consequently, B1-B5 test execution under compositional and geometric demands but cannot establish P2.1's learned zero-shot generalization or adaptation sample efficiency. This distinction was retained even when a baseline performed well.

## Model and Connectome Data

The source is the publicly accessible Pugliese repository at commit `10e7661bf414ba7b4c2edf795cd36d0f878c17c0`, using `W_20260522_allSynapses / wTable_20260522_allSynapses`. We selected DNg100, IN17A001, INXXX466 and IN16B036, together with leg motor neurons in the fl, ml and hl subclasses. This yielded 412 nodes, 2592 directed nonzero edges and 18831 summed absolute synapse counts. All retained edges were preserved without a synapse-count threshold. The table includes measured source IDs and predicted neurotransmitter labels/confidences, retaining missing confidence as unknown.

The selected 18 interneurons include six copies of each CPG type. Historical minicircuit labels differ from current export labels; stable body IDs are used for provenance. The graph contains seven cross-leg edges, whose removal had no observed B1 effect. This small retained set cannot represent the full inter-leg coordination system. There is one biological connectome instance; a degree-preserving randomized graph is a counterfactual topology, not another animal.

The downloaded export does not unambiguously identify its underlying neuPrint release, so we report its exact file version, commit and checksum instead of assigning an unsupported release number. The original brain dataset and female VNC dataset are references, not secretly merged inputs. Zero reconstructed brain neurons are simulated.

## Brain-VNC-Body Architecture

The input is a synthetic symbolic event list with target key and time. Eight synthetic leaky task units encode key identity. Two measured DNg100 axons receive tonic drive, and the retained VNC graph evolves through recurrent rate dynamics. A fixed equal-weight sum of each leg's MN activity gates a downward press. A separate task decoder selects the key position, a limb allocator chooses an available leg, and analytic inverse kinematics supplies joint targets to a torque-limited controller.

This architecture contains a scientifically consequential shortcut: key identity and target timing reach the body decoder without being computed by the measured connectome. The neural readout gates execution but does not generate the full task trajectory. Descending neurons do not directly specify every joint torque; however, the task controller can dominate behavior. That fact is a result of the architecture audit and constrains every interpretation below. The eight task units are not assigned anatomical neuron IDs.

The body is a custom reduced, tethered six-leg model, version `reduced-six-leg-2R-v1.0`, with two rotational coordinates per leg. It integrates torque, angular velocity, unilateral spring-damper key contact and proprioceptive error. It has no flight, free walking, muscle physiology, measured mass distribution or validated adhesion. Mechanical quantities are in model units.

## Experimental Tasks

The registry comprises 96 experiment/condition/variant combinations evaluated with seeds 0-7, for 768 eight-second trials. A1 uses tonic descending drive without periodic external instruction. A2 changes drive magnitude at four seconds; it is an input-amplitude jump, not a calibrated tempo-command or tempo-inference test. A3 removes the symbolic cue between three and five seconds. A4 compares normal, delayed and noisy feedback with feedback removal. A5 changes amplitude, onset and lateral bias.

B1 applies novel synthetic key orders, B2 changes keyboard geometry, B3 disables or forces limbs, B4 varies sequence length/order/timing, and B5 changes reach path or force gains. Eight keys are used in the main batch; the reproduction pipeline also includes a deterministic four-key vertical slice. Sixteen and 88-key tasks were not run. No animal was tested and no copyrighted song entered the benchmark.

Three synthetic sequence identities are reused across the eight seeds. Calibration uses separate seeds 100 and 101, and the initial failed pilots are described in the calibration log. No trainable parameters or optimization steps exist in the benchmark. There is therefore no train/test learning split to validate, and the word held-out refers only to separation from engineering calibration, not a trained model's generalization evaluation.

## Principle 1 Results

The full A1 model produced qualifying motor rhythms in every evaluated seed. Mean spectral concentration was 0.729 (SD 0.082; 95% bootstrap CI 0.671-0.776). CPG, DN and inhibitory-edge lesions, as well as the degree-preserving randomized graph, had zero qualifying rhythmicity. The paired full-minus-no-CPG contrast was 0.729, with paired Cohen dz 8.86 and Holm-adjusted p=7.18e-06. These statistics quantify variability over parameter seeds, not uncertainty over flies.

| Variant | Mean | SD | 95% CI | n |
|---|---:|---:|---|---:|
| full | 0.729 | 0.082 | 0.671 to 0.776 | 8 |
| no_cpg | 0.000 | 0.000 | 0.000 to 0.000 | 8 |
| no_dn | 0.000 | 0.000 | 0.000 to 0.000 | 8 |
| randomized | 0.000 | 0.000 | 0.000 to 0.000 | 8 |
| no_inhibition | 0.000 | 0.000 | 0.000 to 0.000 | 8 |
| no_delay | 0.285 | 0.306 | 0.075 to 0.495 | 8 |

Figure 1 shows every seed-level observation for the principal rhythm and contact analyses. Figure 2 shows actual model traces for four identified core cells. The rhythms arise in the modeled recurrent circuit; rate traces are not recordings of biological firing or generated spike events.

![Core results](figures/core_results.png)

![Identified neural traces](figures/neural_trace.png)

The amplitude-jump analysis gave mean frequency changes of approximately +0.206 Hz for the smaller increase, +0.300 Hz for the larger increase, and -0.642 Hz for the smaller decrease. The larger decrease had no estimable post-jump motor frequency because qualifying oscillatory activity was lost. This is not successful resynchronization. It supports limited drive-dependent modulation while exposing a failure regime.

The A4 contact-recall mean remained 0.53125 across normal, delayed, noisy and removed feedback. Thus the predicted feedback benefit was not demonstrated by the primary contact metric. A weak assumed projection, privileged timing and the body decoder can all account for this insensitivity; it does not falsify proprioceptive stabilization in real flies. Likewise, equal B1 output after the inter-leg lesion does not establish that biological inter-leg coupling is dispensable.

## Principle 2 Results

B1 full-model key accuracy was 0.531 (SD 0.209; 95% bootstrap CI 0.385-0.646), with conditional timing MAE 0.112 (SD 0.002; 95% bootstrap CI 0.111-0.113) seconds. These are contacts generated by body integration, matched one-to-one to targets within a prespecified 0.25-second window. Misses are retained and have undefined timing error rather than zero error.

| Variant | Mean | SD | 95% CI | n |
|---|---:|---:|---|---:|
| full | 0.531 | 0.209 | 0.385 to 0.646 | 8 |
| no_memory | 0.594 | 0.163 | 0.479 to 0.688 | 8 |
| no_cpg | 0.219 | 0.235 | 0.083 to 0.385 | 8 |
| no_feedback | 0.531 | 0.209 | 0.385 to 0.646 | 8 |
| randomized | 1.000 | 0.000 | 1.000 to 1.000 | 8 |
| rnn | 1.000 | 0.000 | 1.000 to 1.000 | 8 |
| hand_cpg | 1.000 | 0.000 | 1.000 to 1.000 | 8 |
| direct | 0.927 | 0.070 | 0.885 to 0.969 | 8 |
| sequence_specific | 0.125 | 0.109 | 0.052 to 0.198 | 8 |

The reach-primitive lesion labeled no_memory achieved mean recall 0.59375, slightly above the full model, instead of the predicted large degradation. Its timing error increased, but that does not rescue the proposed compositional-memory claim. Because the primitives were never learned, the experiment cannot support learning or adaptation efficiency regardless of outcome.

Full-model layout-transfer recall was 0.52083 for a mirrored layout, 0.62500 for a shift, 0.51042 for wider spacing and 0.79167 for changed height. Task-relay states remain context-independent by construction. Their invariance is an engineered property and cannot be presented as an emergent descending-neuron representation. VNC and joint-state differences are reported separately in the representation table. Limb replacement is a rule-based allocator capability; no adaptation trial count is estimable.

## Piano Demonstrations

The controlled motor video is a deterministic replay of B1/full/seed 0, selected by seed index rather than best performance. The ablation video presents full, no-CPG and direct-controller trials with the same synthetic sequence and seed. Audio is synthesized from actual physical contact times, so misses are not concealed by playing a target soundtrack. Both videos contain condition, variant, seed, timestamp, neural-state and contact overlays with provenance sidecars.

No authorized files for Merry-Go-Round of Life or In the Pool were supplied. The two corresponding song videos were not created, and synthetic trials are not relabeled as those works. A local WAV-to-event utility is supplied as a crude auditable onset/spectral-peak baseline; polyphonic transcription and timing-inference accuracy have not been validated.

## Ablation and Causal Analysis

The primary distinction is between necessity for neural rhythmicity and necessity for task success. Removing the CPG abolished A1 motor rhythm, yet no-CPG B1 recall remained 0.21875 on average. The randomized graph and untrained reservoir had no qualifying motor rhythm but reached recall 1.0. A constant or otherwise nonrhythmic drive can therefore support the timed press decoder. The observed piano result is insufficient evidence that the measured CPG generates the sequence.

The direct and hand-CPG baselines replace the body drive while retaining a shadow neural simulation for comparison. Their anatomical rate traces must not be interpreted as causing their body movements. Variant-specific replay graphs now apply the actual lesions and rewiring, rather than drawing the intact graph for every condition. RNN states are synthetic slots without anatomical identities.

The matched-state RNN is not trained. The sequence-specific controller uses a fixed ordering rather than an optimized memorization baseline. These comparisons are useful shortcut diagnostics, but they are not a fair sample-efficiency competition with trained controllers. No decoder-only superiority or biological learning conclusion is generalized beyond this benchmark.

## Generalization

The suite includes short, longer, repeated, nonrepeating, alternating and syncopated symbolic conditions, as well as geometric and limb constraints. All per-run results are available, including failed contacts. Nevertheless, no learned primitive representation, held-out biological connectome, large sequence corpus or calibrated novel-tempo inference exists. The strongest justified term is execution transfer within an engineered system.

Within a condition, parameter seeds are paired across ablations. Reusing three sequence identities across seeds means that treating 96 seed-sequence contacts as 96 independent samples would be invalid. Confidence intervals use run-level seed values and do not estimate population-level sequence or animal variability. The manuscript therefore does not claim broad compositional generalization.

## Reproducibility and Open Science

The repository includes source-fetch/preprocessing scripts, an experiment registry, seed and parameter metadata, checksummed raw telemetry, analysis scripts, editable figure sources, a replay interface, video renderer, dependency lock and Windows reproduction wrappers. The core pipeline verifies deterministic execution, neural negative controls, geometric contact and output ranges. The clean-checkout audit records actual execution status and differences; it is authoritative over any aspirational reproducibility statement.

The public MANC export repository did not expose an explicit license in the inspected snapshot, while anatomical assets come from the GPL-licensed malevnc package. The software license cannot grant rights to third-party data. No public code/data deposit or DOI has been created. A local Git tag is not an archival public release. PLOS Computational Biology's code and data availability requirements therefore remain unmet [PLOSCode; PLOSData].

## Limitations

The model contains no reconstructed brain neurons, no anatomically registered brain-VNC bridge and no neuron-specific arbor mesh. Its 3D surface is real MANC anatomy, but activity is aggregated by soma neuromere, not by verified arbor occupancy. Structural paths are not inferred causal propagation paths. A rate model cannot supply spike timing, and the display correctly uses a rate raster.

Predicted neurotransmitters, volume-based gain normalization, uniform weight scaling, assumed sensory projections, fixed delays and the reduced body all introduce uncertainty. The graph omits most VNC interneurons, sensory afferents, modulatory systems and detailed neuromuscular mappings. It cannot establish how a fly normally walks, learns, hears a melody or selects a limb.

Forward Euler integration at 2 ms is an approximation. For seed 0 under tonic drive and fixed 4 ms delay, the mean oscillatory-MN frequency was 8.771 Hz at 2 ms, 9.021 Hz at 1 ms and 9.300 Hz at 0.5 ms. The coarse result is about 5.7% below the finest tested value; high-precision numerical convergence is not established. All headline effects should be interpreted at the tested resolution.

The body controller receives privileged key identity and timing, the symbolic relay is context-free by design, and the primitive lesion is not a plasticity lesion. These are major scientific limitations, not cosmetic caveats. Small sample sizes, one connectome, sparse task diversity and untrained baselines further limit inference. The full original mission remains incomplete.

## Discussion

The most useful finding is the dissociation between neural rhythm and task execution. The chosen recurrent motif can support persistent oscillations under tonic drive, and circuit lesions expose that dependence. Yet the keyboard task rewards a decoder that already knows what to press and when. Replacing patterned neural output with a sufficiently strong alternative drive can improve contact recall. A visually persuasive piano demonstration could therefore be scientifically misleading without the ablations and explicit shortcut audit.

A stronger next model would route task variables through identified brain/descending circuitry, constrain the MN-to-muscle mapping, and compare trained primitive composition against capacity-matched alternatives. It would require a richer measured premotor/sensory subgraph, a validated body model, more independent sequences and connectome instances, and prospective thresholds for recovery and invariance. These extensions are requirements for the original claims, not results of the present study.

## Conclusion

This executed feasibility benchmark supports a restricted model-level account of descending-drive-dependent VNC rhythmicity. It does not establish learned motor primitives, task-space invariance arising from biology, or a connectome-specific advantage in key execution. Transparent negative findings, raw telemetry and variant-correct replay provide a basis for redesigning the architecture before making stronger embodied-neuroscience claims.

## Methods

The full equations, distributions, integration scheme, contact model, readout, intervention definitions and metric formulas are in the methods appendix. Briefly, each rate relaxes toward a rectified saturating tanh of signed recurrent and external input. Per-cell gain and threshold scale inversely and directly with relative volume, respectively. Evaluation seeds draw positive-clipped gains, thresholds, rate caps and time constants; they do not change the measured graph except in the randomized condition.

Directed double-edge swaps preserve incoming and outgoing degree and outgoing weighted strength, but not postsynaptic strength or spatial wiring cost. Source synaptic signs remain attached to their presynaptic cells. CPG/DN/intra-leg/inter-leg/inhibitory/delay/body-mapping interventions have explicit code paths. Contact detection uses simulated geometry and force with no target-event insertion.

We report mean, median, SD, seed-bootstrap confidence intervals, paired standardized differences and two-sided paired t-tests. Holm correction covers the available family of 185 primary contrasts. Missing timing values and zero-variance effect sizes are left undefined. Tests are exploratory because parameters were calibrated before the main batch and the design was not independently preregistered. No results were excluded for being unfavorable.

## Data and Code Availability

Local code is in the project repository; complete computational observations are under data/runs, aggregate and per-run tables under paper/tables, and source hashes under connectome_manifest.json. The reproduction scripts fetch the exact public source snapshots. Public redistribution permission for the source export must be resolved, and a public repository, archival identifier, author list and persistent data deposit must be supplied before journal submission. The two copyrighted-song demonstrations remain pending authorized inputs.

## References

[Dorkenwald2024] Neuronal wiring diagram of an adult brain. 2024 peer-reviewed Nature article. https://www.nature.com/articles/s41586-024-07558-y

[Shiu2024] A Drosophila computational brain model reveals sensorimotor processing. 2024 peer-reviewed Nature article. https://www.nature.com/articles/s41586-024-07763-9

[Azevedo2024] Connectomic reconstruction of a female Drosophila ventral nerve cord. 2024 peer-reviewed Nature article. https://www.nature.com/articles/s41586-024-07389-x

[Pugliese2026] Connectome simulations identify a central pattern generator circuit for fly walking. 2026 bioRxiv preprint, April 30 2026 revision; not journal-peer-reviewed in the consulted record. https://pubmed.ncbi.nlm.nih.gov/42094485/

[Cheong2026] Organization of circuits linking descending input to motor output in the Drosophila Male Adult Nerve Cord connectome. 2026 eLife Version of Record, July 20 2026. https://elifesciences.org/articles/96084

[WangChen2024] NeuroMechFly v2: simulating embodied sensorimotor control in adult Drosophila. 2024 peer-reviewed Nature Methods article. https://pubmed.ncbi.nlm.nih.gov/39533006/

[FlyGM2026] Whole-Brain Connectomic Graph Model Enables Whole-Body Locomotion Control in Fruit Fly. 2026 arXiv preprint; v3 full-text passages consulted, publication status not independently established. https://arxiv.org/abs/2602.17997

[Larval2026] A canonical excitatory-inhibitory motif embedded in the connectome underlies rhythmic locomotion in Drosophila larvae. 2026 preprint abstract indexed August 31 2026; full text not verified. https://doi.org/10.64898/2026.08.31.748252

[PLOSCode] PLOS Computational Biology code availability policy.  journal policy. https://journals.plos.org/ploscompbiol/s/code-availability

[PLOSData] PLOS Computational Biology data availability policy.  journal policy. https://journals.plos.org/ploscompbiol/s/data-availability

