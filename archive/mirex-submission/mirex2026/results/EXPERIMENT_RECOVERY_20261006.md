# MIREX experiment recovery — 2026-10-06

This is a handoff inventory, not an official MIREX score sheet. The nine-metric
GTZAN/SMC table is in [the MIREX README](../README.md) and its frozen source
CSV files are in [`target_table_20261005/`](target_table_20261005/). Their
published SHA-256 values were rechecked on 2026-10-06. The CSV grain is one
model × dataset × decoder row; each listed model has four decoder rows per
eligible dataset. The upstream BeatThis `final0` has GTZAN-only rows because
it trained on SMC and must never be scored on full SMC.

| Experiment | Training pool | Recovered state | Submission use |
|---|---:|---|---|
| BeatThis seed 2, 120 epochs | 4,339 allowed log-Mel pieces; SMC/GTZAN excluded | Complete; final checkpoint SHA-256 `0fed3858ac75ec716e622c0a5bd50ee1345fb1443902d3024ecff5e88fa20053` | Primary for both beat and downbeat |
| MSCNN seed 0, 1,500 epochs, split | 3,783 train + 556 allowed validation | Complete; selected epoch 1499 SHA-256 `6cb647407caf367e1e3e66d13061a4459899f26e1ae0001e5c519cac95ab30b1` | Runnable secondary until full retrain passes checks |
| MSCNN seed 0, 1,500 epochs, full | 4,339 allowed log-Mel pieces; SMC/GTZAN excluded | Kaya job `74883` timed out after epoch 899; its checkpoint SHA-256 is `48d1bfb1f55b87424c5999683169df733df1b762d88eec143e67c22b6a94fb8c`. Job `75204` failed on restricted PyTorch checkpoint loading. Job `77798` restored model, optimizer, and scheduler at epoch 900 and is running. | **Not yet eligible**; no completed weight or table scores |
| TCN seed 0, split and full | 3,783 and 4,339 allowed log-Mel pieces | Both complete with frozen historical diagnostics; follow-up paused | Not in the current three-backbone MIREX package |
| BeatFM 911 and 1,684 mapped-WAV pools | 774/137 and 1,431/253 train/allowed-val split | Both training runs complete. The 911-pool epoch-15 checkpoint was allowed-validation selected; the expanded pool's matched-panel comparison was stopped. No target-set matrix scores exist. | Reduced-data private fallback only; source/MERT rights unresolved |
| SpecTNT | No training pool instantiated | Not implemented; no job or checkpoint | Placeholder only |

The existing target-set figures were produced historically after clean
checkpoint decisions were frozen. MIREX 2026 forbids GTZAN/SMC for *any*
development purpose, so they are quarantined: they cannot select a model,
decoder, seed, epoch, or submitted variant. The clean BeatThis choice is
documented in the [556-piece allowed-validation panel](beatthis_seed2_allowed_panel_20261004/README.md).
That panel is a development comparison, not an unbiased estimate of the later
4,339-piece retrain. The full MSCNN row stays `—` until training finishes and
an allowed-data smoke/provenance audit passes; it must not inherit the split
checkpoint's metrics.

The private task-specific candidates are
`submission-builds/casm-mirex2026-beat-beatthis-mscnn-20261006.tar.gz`
(SHA-256 `df031739087ab8b6f3906144b3536735bd2cf4c992cd92d5ca264beef6efd0c3`)
and `submission-builds/casm-mirex2026-downbeat-beatthis-mscnn-20261006.tar.gz`
(SHA-256 `e5a002ddc4760c6a46d2ec303c66becec2b7cad90748c3d65ce26a23e6b53fc5`).
Their READMEs each specify exactly four organizer commands for one task, so
MIREX's README scanner cannot accidentally evaluate downbeats as beats or
vice versa. The internal dual-task smoke bundle is
`submission-builds/casm-mirex2026-dual-task-beatthis-mscnn-20261006.tar.gz`
(SHA-256 `589959ff446470135408c5848a1b54e62d584a5be74aa4bb79096b2c184c9d67`).
Its manifest specifies separate `--task beat` and `--task downbeat` commands,
contains BeatThis and the disclosed MSCNN split checkpoint, and excludes
BeatFM. All 48 manifest-listed files passed SHA-256 verification. The
extracted Linux bundle was smoke-tested on an allowed WAV: BeatThis+CASM
produced 44 beats and 15 downbeats; MSCNN+Direct produced 15 downbeats.
This is a **submission candidate**, not an organizer-uploaded entry.
