# MIREX integration status

This file is the handoff boundary between running experiments and the final
submission bundle. A model is enabled in `config/backbones.json` only after
all required fields below are frozen and its one-WAV smoke test passes.

As a fallback while BeatFM expanded-data comparison and source redistribution
rights remain open,
`submission-builds/casm-mirex2026-beatthis-mscnn-fallback-v2-20261004.tar.gz`
contains the selected BeatThis and MSCNN checkpoints but **no BeatFM source,
MERT weights, or checkpoint**. Archive SHA-256:
`9e2a435990bb98dd71c2bc7ca7bff1725ec4eb3c68e98aeea36a20814531a1d9`.
It was copied, hash-checked, extracted, and run on lab5090: BeatThis+CASM
returned 44 beats, MSCNN+Direct 42 beats on the real allowed smoke WAV. This
is a runnable candidate bundle, not an uploaded MIREX entry.

## BeatThis — primary

- [x] Upstream/fork source located and revision recorded
  (`b95c8ab0c58c2d9fcfd40508ae8dffbc05ac4f5c`).
- [x] Original Direct postprocessor matched: seven-frame local maxima,
  logit threshold zero, plateau averaging, downbeat-to-beat snapping, and the
  original raw-downbeat behavior when no beat peak exists.
- [x] Audio-to-logit adapter implemented.
- [x] No-SMC, GTZAN-held-out 100-epoch seed-0 baseline completed with exit 0;
  checkpoint hashes and epoch inventory recorded.
- [x] First [disjoint diagnostic](results/BASELINE_DIAGNOSTIC.md) rebuilt;
  official final0 is evaluated on GTZAN only.
- [x] Seed-0 100-epoch single-split checkpoint screen and clean Beatles
  epoch-79 provisional choice recovered with raw tables and hashes.
- [x] Expanded 200-epoch, three-seed allowed-validation search complete on
  2026-09-30. The allowed Beatles validation chose seed 2, zero-based epoch
  119; the selected search checkpoint SHA-256 is
  `cd8a8c93b11c189daab497076261730bc8a059fa2b8d2b9c07b012c2d9c4bd4d`.
- [x] Allowed-validation checkpoint/seed decision frozen before SMC/GTZAN
  target inspection.
- [x] Winning seed retrained for 120 epochs on all allowed development data;
  the lab run records `TRAINING_COMPLETE` and checkpoint hashes.
- [x] Final checkpoint copied privately to `weights/beatthis.ckpt` (SHA-256
  `0fed3858ac75ec716e622c0a5bd50ee1345fb1443902d3024ecff5e88fa20053`)
  and one-WAV Direct/CASM/both-DBN smoke-tested on lab5090.

## MSCNN — secondary

- [x] One seed-0 training run retained.
- [x] Additional seed expansion cancelled by project decision.
- [x] Exact preprocessing and checkpoint loader audited.
- [x] Shared `Audio2Frames` adapter verified by loading an MSCNN checkpoint and
  running a finite 50 Hz beat/downbeat-logit forward pass.
- [x] Seed-0 training complete (1,500 epochs on Kaya; job `39249`).
- [x] Seed-0 four-candidate allowed-validation screen complete on lab5090;
  the Beatles-only Direct formula selected last epoch 1499. The earlier job
  `39261` failure is historical. See the [audited table](results/mscnn_seed0_allowed_screen_20261004/README.md).
- [x] Chosen train-split checkpoint copied privately to `weights/mscnn.ckpt`
  (SHA-256 `6cb647407caf367e1e3e66d13061a4459899f26e1ae0001e5c519cac95ab30b1`)
  and one-WAV Direct smoke-tested on lab5090. No full-allowed retrain yet.

## BeatFM — 911-piece candidate selected; expanded training and rights pending

- [x] User-supplied source archive SHA-256 and private Kaya/Gadi copies
  recorded. The archive's embedded Git metadata has no resolvable commit.
- [ ] BeatFM-source redistribution permission checked. The pinned MERT model
  card lists CC BY-NC 4.0; see [third-party notes](THIRD_PARTY.md).
- [x] Isolated Kaya and Gadi dependency directories with Transformers 4.45.1
  and pinned MERT95M snapshots; existing PyTorch environments untouched.
- [x] Real WAV loading, MERT 24 kHz resampling, 15-second clips, aligned
  75 Hz training targets, and pinned-source head tested in a one-epoch
  engineering pilot (Kaya job `45587`, exit 0). The source discrepancy is
  documented in
  [the audit](backbone-retrain/BEATFM_SOURCE_AUDIT.md).
- [x] Source model inference entry point identified and synthetic-waveform
  forward smoke-tested on 5090 (inference only; no trained checkpoint).
- [x] A 75 Hz to 50 Hz beat/downbeat-logit adapter implemented and registered;
  real Ballroom WAV plus engineering-pilot checkpoint produced 1,590 finite
  50 Hz frames on lab5090 (inference only). This is not an accuracy test.
- [x] No-SMC, GTZAN-held-out split preflight: 3,783 train / 556 allowed val.
- [x] Strict manifest builder and isolated training entry point prepared;
  5090 is reserved for inference, not BeatFM training.
- [x] Ballroom (685) and RWC 2.0 (226) original WAVs mapped with source
  checksums, duration and annotation-alignment checks. The 911-piece
  Ballroom/RWC verified-subset candidate (774 train / 137 allowed val) is
  completed on Kaya as job `45647` with full 15-second/5-second-overlap
  training clips (22 epochs, early stop). It is not the equal-data BeatThis
  comparison. Best validation-loss checkpoint SHA-256:
  `174c4b056b47e344eb841de5f6025581cd8e7f2362a5aafb99a7d3bfe63892cb`.
- [x] The trained 911-piece checkpoint plus original WAV was independently
  smoke-tested on lab5090 and Gadi: both produced 29 beats, first at 0.300 s.
  This is a runtime check, not a performance estimate.
- [x] Five checkpoints × Direct/CASM/two-DBN scored on the same 137
  allowed-validation Ballroom/RWC recordings on lab5090 (inference only).
  The private WAV transfer, original split manifest, per-piece IDs, and
  checkpoint hashes were verified. The predeclared Direct beat composite
  selected epoch 15 (SHA-256
  `44a1a33f6c3d08180bea2f0619c16a39a756644f101d0cd5d1691f7abd8ba764`);
  see the [raw table](results/beatfm/README.md) and
  [exact common-panel comparison](results/common_allowed_137_20261004/README.md).
  Kaya launchers `69059`/`69065` failed before scoring; queued duplicate
  `69069` was cancelled after the 5090 result completed and generated no
  scores. Training and checkpoints were unaffected.
- [x] A separately identified 1,684-piece original-audio subset was mapped
  (1,431 train / 253 val; manifest SHA-256
  `92e1ef0c4a02dc7d52b671966dcc7bc333e9bb55e66a609688a674ae282aeef`)
  and Kaya job `69061` running. Groove annotations extending beyond audio
  are clipped by the trainer and require disclosure in its result table.
- [x] Kaya job `69066` is dependency-linked to successful completion of
  `69061`; it will score five expanded checkpoints on the **same 137-piece
  Ballroom/RWC validation panel** used for the 911-piece candidate. The
  expanded-only 253-piece panel is a separate follow-up, not interchangeable
  with the common panel.
- [ ] Original audio mapped for all 4,339 allowed pieces; the BeatThis data
  view only contains spectrogram caches, so full-data reproduction remains
  blocked.
- [x] Provisional three-backbone private bundle exercised on lab5090: BeatFM
  and MSCNN each returned valid one-WAV output under Direct, CASM, DBN
  55–215, and DBN 30–300. BeatFM Direct output SHA-256
  `8eefe395392bf81596175146bd0f4c1af94226b29731fea36cfeba5edc20a74a`
  exactly matched the independent Gadi run. This tests packaging/runtime,
  not BeatFM model selection or accuracy.
- [x] Allowed-validation-selected BeatFM epoch-15 checkpoint copied privately
  to `weights/beatfm.ckpt`, SHA-256 verified, and bundled with BeatThis and
  MSCNN in
  `submission-builds/casm-mirex2026-three-backbone-911-selected-20261004.tar.gz`
  (archive SHA-256
  `cb7863c4719eac6e21bc84e1aca69eef1cd114bba128ccbca7cd9846085ae23d`).
  The extracted archive passed lab5090 one-WAV Direct/CASM/both-DBN checks
  for BeatFM (34/34/43/43 beat times), plus BeatThis+CASM and MSCNN+Direct.
  This is a **private selected 911-piece candidate**, not the final official
  entry while expanded-data evidence and source rights remain open.

BeatFM is runnable with the selected 911-piece train-split checkpoint and
audited private source/MERT files, but expanded-data comparison,
full-allowed-subset retraining, and distribution rights remain open. The
bundle builder includes the source,
MERT snapshot, architecture module, and pinned dependency only when BeatFM is
explicitly supplied; missing assets fail closed.

## Decoder contract

- `direct`: original BeatThis local-maxima rule, without a tempo prior.
- `dbn`: 55–215 BPM by default; `--dbn-wide` selects 30–300 BPM.
- `casm`: frozen no-SMC configuration at 30–300 BPM.

All three decoders consume one-dimensional, finite beat and downbeat logits at
the frame rate declared by the backbone registry. MIREX output contains one
strictly increasing beat time in seconds per line.
