# MSCNN-lite no-SMC checkpoint screen provenance

- Training data view: `views/no_smc_20260929/data`, official `single.split`; no `--fold`.
- Observed training names/loaded: 3784/3783; validation: 556/556.
- Train and validation contain neither SMC nor GTZAN. GTZAN is test-only.
- GTZAN annotation names/loaded: 999/993. Six empty/invalid jazz files are skipped: jazz_00003, jazz_00009, jazz_00010, jazz_00014, jazz_00018, jazz_00020.
- Annotation support repository commit: `aca41a23a26881ba3d1e5b5e4bc3f4869d6a3ed7`.
- no-SMC single-split manifest SHA256: `ad507613256b7ccb69fa2cd206c47c27b3887dde065f7b2452c069a2338bdc03`.
- no-SMC annotation-tree SHA256: `1b564f8ed6072cbb57f93b0475f106972020ff99d0f668d769284b4e8ce1a42c`.
- Candidate pool is retained val-loss top-3 + every-100-epoch milestones + last. Logical checkpoint identity/full-file SHA are preserved, while inference is de-duplicated by normalized state_dict tensor bytes.
- Candidate selection uses Direct/minimal decoding. SMC+GTZAN oracle is diagnostic and explicitly submission-ineligible.
- Clean selection is frozen from the allowed-validation Beatles subset only: 60% beat + 40% downbeat, with each target 50% F + 25% CMLt + 25% AMLt.
- Only the frozen clean role is submission-eligible. Best-val and last are conditional on predeclaration before target inspection; oracle is never eligible.
- Missing/non-finite F/CMLt/AMLt fails selection/reporting; SMC requires beat only. JSON uses null rather than NaN.
- StructBeat CASM full-7F is permitted only after the three-piece event/byte equivalence gate against exact icassp2027casm/casm v0.1.0 config SHA256 82f84521605c19a02c81ddda3aba50983c9ac0cd9243595d4cb24973ac9946de.
- All selected-role caches are reused for Direct, CASM release-7F, default DBN, and DBN 30-300.

- Slurm job: `39261`; node: `k014`; started: `2026-09-29T16:42:01+08:00`.
- `submission_choice.json` is atomically frozen from allowed validation before any SMC/GTZAN cache is created.
