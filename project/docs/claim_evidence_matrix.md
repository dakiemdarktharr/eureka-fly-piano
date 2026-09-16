# Claim-evidence matrix

| Claim | Evidence | Figure/table | Status and limitation |
|---|---|---|---|
| The implemented graph contains 412 measured neurons | Source IDs, pinned export and extraction | manifest; neurons.csv | Supported; only 2 DN axons, 18 CPG and 392 MNs |
| Tonic input supports modeled motor rhythm | All eight A1 full runs | core_results; per_run.csv | Supported under calibrated rate-model assumptions |
| CPG/DN lesions eliminate this sustained neural rhythm | Eight paired A1 runs per variant | contrasts.csv | Supported within this reduced network, not an animal necessity claim |
| Stronger drive always yields the desired tempo | A2 drive jumps | extended_metrics.csv | Not established; no desired-tempo calibration; large down-jump loses rhythm |
| Feedback stabilizes piano execution | A4 normal/delay/noise/removal | summary.csv | Not demonstrated in contact recall; all means 0.53125 |
| The connectome improves key execution over alternatives | B1 alternatives | core_results | Not supported; several simpler/nonanatomical controllers outperform full |
| Primitive memory is necessary for novel sequence recall | B1 reach-primitive lesion | contrasts.csv | Not supported; lesion mean recall exceeds full; not a genuine memory lesion |
| The model learns primitives | No training code or training results | configuration; methods | Unsupported; prohibited in title and abstract |
| Task-state invariance emerges from neural biology | B2 representation distance | representations.csv | Unsupported; relay invariance is imposed by its input and architecture |
| Limb reassignment is possible | B3 rule-based allocator conditions | per_run.csv | Engineering execution only; no learned adaptation claim |
| A complete brain-VNC-body fly was simulated | Graph scope and custom body | manifest | False; zero reconstructed brain neurons, reduced tethered surrogate |
| Every visible rate/contact is recorded simulation data | Hash-checked replay and contact arrays | videos and metadata | Supported, subject to documented within-step timestamp convention |
| Exact neuronal anatomy is highlighted | Anatomy mapping audit | anatomy.json | Not achieved; regional mesh plus separate schematic neuron graph |
| Code/data meet journal public-access requirements | Local repository only | reproducibility audit | Not achieved; no public deposit/DOI and unresolved export license |

The strongest result is a dissociation between circuit rhythm and decoder-supported
task success. The full project claim in the original brief remains a research target.
