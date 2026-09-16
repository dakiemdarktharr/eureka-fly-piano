# Eureka motor-control benchmark

An executed **feasibility study**, not a completed brain-piano research system.
The model uses 412 measured MANC neurons (2 descending, 18 CPG, 392 leg motor),
plus eight engineered symbolic task-relay states and a six-leg dynamical surrogate.
There are zero reconstructed brain neurons. The body is not NeuroMechFly.

768 registered runs cover A1-A5 and B1-B5, 15 controller/ablation variants and
eight parameter seeds. Every condition is retained. Three synthetic sequence
identities are reused across seeds; there is one biological connectome instance.

The recorded results support tonic-input rhythm generation under this model's
assumptions. The full controller's B1 key accuracy is 53.125%, while the hand CPG,
randomized graph and untrained reservoir reach 100% in this simple task. These
outcomes expose decoder-dominated execution; they do not establish learned
primitive reuse or a connectome advantage. See `paper/manuscript.md` and the audits.

## Run on Windows

Python 3.11+ and ffmpeg on PATH are required. From this folder:

```powershell
.\reproduce_core.ps1
.\reproduce_all.ps1
.\.venv\Scripts\python.exe app\server.py 8765
```

Open http://127.0.0.1:8765. The interface is read-only unless the explicit
experiment-run button is used. No model parameter changes occur during replay.
The server binds only to loopback.

Individual commands after environment setup:

```powershell
# One experiment
.\.venv\Scripts\python.exe experiments\run.py --id A1_tonic_full_s00
# All tables and core figures from existing telemetry
.\.venv\Scripts\python.exe analysis\summarize.py
.\.venv\Scripts\python.exe analysis\extended.py
# One replay JSON (or use the interface export button)
.\.venv\Scripts\python.exe visualization\replay.py B1_novel_full_s00
# Regenerate the synchronized videos
.\.venv\Scripts\python.exe visualization\video.py
# All unit tests
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
# Regenerate the complete feasibility manuscript
.\.venv\Scripts\python.exe paper\build.py
```

For Linux: create a Python 3.11 environment, `pip install -r environment.lock`,
install ffmpeg, then `OPENBLAS_NUM_THREADS=1 python reproduce.py core`.
The Dockerfile is supplied, but its build is not represented as tested unless
the reproducibility audit explicitly records a Docker run.

## Data and provenance

`connectome/prepare.py` fetches pinned public source artifacts and streams the
compressed dense matrix, avoiding a full 4.47 GB allocation. Downloads and
derived anatomy are local; source hashes and license status are in
`connectome_manifest.json`. The export's underlying neuPrint release is not
asserted because the downloaded artifact does not establish it.

`data/runs/<ID>/` contains full-rate neural/body telemetry, metadata, contacts,
events and metrics. `paper/tables/per_run.csv` includes every run; summary CIs
resample seeds, not biological individuals. `experiments/registry.json` freezes
the evaluated conditions. Calibration is separate and documented.

`docs/sources/verified_sources.json` lists verified primary references and
publication status. The CPG source is a preprint. Related whole-brain trained
graph-controller work exists; no broad novelty claim is made.

## Deliverables and remaining gates

- Manuscript source/PDF, methods appendix, supplementary tables, figures, cover
  letter draft, risk checklist and three-perspective internal review.
- Interactive anatomical VNC view, neuron/edge inspector, physical body replay,
  task relay, timeline, rate raster, metrics and two synthetic videos.
- No authorized Hisaishi/Ushio files: those two named song videos remain pending.
- No learned primitive memory, matched trained RNN, polyphonic transcription,
  physiological parameter validation, exact neuron meshes, or brain-VNC bridge.
- No public deposit or DOI. Source-export licensing and author metadata remain
  unresolved. Do not treat a local tag as an archived public research release.

The software is runnable and the negative findings are useful. The full original
scientific mission is **not complete** and the manuscript is **not submission-ready**.
