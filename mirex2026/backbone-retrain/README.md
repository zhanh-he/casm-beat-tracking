# Why MIREX backbones are retrained

The ICASSP paper's BeatThis evaluation uses eight fold-specific backbone
checkpoints. Each SMC piece is predicted by a checkpoint that held out its
fold; the rest of SMC may still be present in that checkpoint's training.
That is appropriate for the paper's cross-validation protocol, but not for
a MIREX 2026 competition model, which may not use SMC or GTZAN for *any*
development purpose.
The upstream BeatThis `final0` checkpoint also trained on SMC, so its full-SMC
score is training-set leakage, not a valid benchmark.

For MIREX, we therefore retrain the upstream BeatThis architecture and
training recipe with SMC and GTZAN excluded from backbone development. We
select seed, epoch, and decoder using only allowed validation pieces. After
freezing those decisions, the intended final model is retrained on the full
allowed pool, still excluding SMC and GTZAN. This is a different checkpoint
and data protocol, not a repeat of the ICASSP paper submission. CASM's
MIREX-specific no-SMC calibration is in `../config/casm-no-smc.json`; the
standalone public 7F decoder is a separate paper/release configuration.

## What is present

- [`train_beatthis_final_nosmc.sh`](train_beatthis_final_nosmc.sh) records the
  upstream-derived seed-0, 100-epoch no-SMC baseline command, including
  provenance hashes and milestone checkpoints. It expects a prepared data
  view and lab environment; it is not the frozen winning final-retrain recipe.
- BeatThis is the primary candidate. MSCNN is now the highest-priority
  remaining retrain; TCN work is paused and SpecTNT remains unimplemented.
  The [BeatFM source audit and raw-audio gate](BEATFM_SOURCE_AUDIT.md)
  records the supplied archive, code/paper discrepancies, exact no-SMC split,
  and the separately sourced original audio.
- [`beatfm_manifest.py`](beatfm_manifest.py) will write the complete original-
  audio manifest only when all 4,339 allowed pieces resolve. It also permits
  an explicitly named 911-piece Ballroom/RWC verified-subset candidate; this
  is MIREX-eligible if disclosed, but not an equal-data BeatThis comparison.
  The separate
  [`train_beatfm.py`](train_beatfm.py) uses the user's private BeatFM head source
  and pinned MERT95M, with 15-second clips/5-second overlap for full data,
  allowed-validation loss, periodic hash-recorded checkpoints, and a
  fixed-epoch all-allowed-data mode. It
  rejects unmarked partial manifests by default. The 911-piece verified
  subset completed as Kaya job `45647`; the 1,684-piece expanded subset is
  a separately completed Kaya job `69061` (25 epochs, early stop). The
  911-piece candidate's five-checkpoint
  allowed-validation screen selected epoch 15; see the
  [score table](../results/beatfm/README.md). The 1,684-piece run still
  has no completed final metric screen: `69066` failed before scoring due to
  a staging-path error, and retry `70943` was cancelled on 2026-10-05 at the
  user's request to stop BeatFM experiments. Existing weights and logs were
  retained. Both runs require reduced-data disclosure.
- Verified RWC 2.0 and Ballroom original-audio mapping is documented in the
  [audit](BEATFM_SOURCE_AUDIT.md). [`rwc2_audio_map.py`](rwc2_audio_map.py)
  checks CD/track metadata, WAV duration, and every beat timestamp;
  [`ballroom_audio_map.py`](ballroom_audio_map.py) checks WAV duration and
  exact cross-split duplicates. Explicit `--pilot-partial-audio` flags allow
  an engineering smoke run on 700 verified pieces, but such a checkpoint
  is tagged **not for submission** and cannot be called full-data training.
  `--verified-subset` uses all 911 mapped pieces with the paper's sliding
  clips and a separate provenance tag.
- [`harmonix_source_index.py`](harmonix_source_index.py) joins all 911 public
  Harmonix labels to the dataset's metadata-only video URLs and published
  alignment scores. It does **not** acquire or verify original audio.
- The primary BeatThis's seed/epoch decision, full-allowed-data retrain,
  checkpoint hash, and one-WAV smoke are complete; see
  [`../INTEGRATION_STATUS.md`](../INTEGRATION_STATUS.md). BeatFM's provisional
  best-loss checkpoint passed one-WAV runtime checks on lab5090 and Gadi;
  its **different, selected epoch-15 weight** has an allowed-validation score
  but awaits final package smoke testing and expanded-data comparison.
  No script or README here asserts that MIREX has received a submission.
- [`run_mscnn_full_allowed_seed0.sbatch`](run_mscnn_full_allowed_seed0.sbatch)
  and its [CUDA race launcher](run_mscnn_full_allowed_seed0_cuda.sbatch) freeze
  the selected seed-0, 1,500-epoch MSCNN recipe and merge the 3,783 training
  plus 556 allowed-validation pieces with `--no-val`. Both launchers hard-fail
  unless the effective loader contains exactly 4,339 pieces and zero SMC or
  GTZAN training items. Kaya jobs `74765` (MI210 backup) and `74883` (V100)
  were submitted on 2026-10-05; their output directories are separate.

Never evaluate a checkpoint on pieces used for its training. The gate and
corrected diagnostic are documented in [`../scripts/`](../scripts/) and
[`../results/`](../results/).
