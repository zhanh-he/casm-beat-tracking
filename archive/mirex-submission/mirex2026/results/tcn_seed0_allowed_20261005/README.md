# TCN seed-0 allowed-validation screen — 2026-10-05

Kaya training of the TCN on 3,783 no-SMC, no-GTZAN BeatThis log-Mel pieces
completed all 120 epochs. One empty Beatles beat annotation was skipped. The
frozen 556-piece validation split was then used to evaluate nine distinct
checkpoint states with Direct, **without reading SMC or GTZAN**. The
pre-existing selection rule (60% Beatles beat / 40% Beatles downbeat, each
combining F/CMLt/AMLt as 50%/25%/25%) selected zero-based epoch 119, file
`milestone-119.ckpt`, SHA-256
`4b55dd02e63560bbc06b6800f48cf3c1eeac21b4af003a9f82f4b86fdb395b4f`.
The `last.ckpt` container has different file bytes but the same tensor-state
hash; it was not evaluated twice. The
[`submission_choice.json`](submission_choice.json) and
[`checkpoint_manifest.csv`](checkpoint_manifest.csv) retain the exact choice
and all candidate hashes; `candidate_screen/` retains the nine Direct
validation summaries and their per-piece rows.

The selected checkpoint's logits were reused for all four decoder runs on
the **same** 556 validation pieces (four CSVs with 556 unique rows each).
Values are piece-macro beat percentages, not independent test scores.

| Decoder | F1 | CMLt | AMLt |
|---|---:|---:|---:|
| Direct | 87.54 | 73.89 | 78.45 |
| CASM, frozen no-SMC 30–300 | **87.98** | **75.53** | 80.61 |
| DBN 55–215 | 84.62 | 73.69 | **84.06** |
| DBN 30–300, exploratory | 84.17 | 73.06 | 83.98 |

CASM is the frozen no-SMC configuration from
[`../../config/casm-no-smc.json`](../../config/casm-no-smc.json), not a
TCN-specific or SMC-tuned decoder. The source `.summary.json` and
`.pieces.csv` files beside this README are preserved, as is the batch recipe
[`../../backbone-retrain/run_tcn_allowed_only.sbatch`](../../backbone-retrain/run_tcn_allowed_only.sbatch).
The final 4,339-piece no-validation retrain is a **different** checkpoint and
must not inherit this validation table as its own performance estimate.
