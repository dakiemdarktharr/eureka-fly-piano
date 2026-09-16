# Videos

`controlled_motor_tests.mp4` replays B1 / novel / full / seed 0.
`ablation_comparison.mp4` shows full, no CPG and direct controller trials consecutively,
using the same input sequence and seed, and the same fixed activity scales.
Audio is a generated sine tone at each actual physical key contact. It is not target
audio and does not hide missed or extra contacts. Frames are selected by raw timestep.

Each MP4 has a JSON sidecar with complete run metadata and its checksum. Video pixels
carry experiment, variant, seed, time, source revision, dataset and config digest.

`piano_merry_go_round.mp4` and `piano_in_the_pool.mp4` are **not produced**: no authorized
audio/MIDI files were supplied. The synthetic tests are not represented as those works.

Re-render: `python visualization/video.py` from the project root.
