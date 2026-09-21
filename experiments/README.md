# Reproducing the eight-fold evaluation

The public evaluator expects one `.npz` per piece with these keys:

- `piece`, `dataset`, and `has_downbeats`;
- `beat_logits` and `downbeat_logits` at 50 Hz;
- `truth_beat` and `truth_downbeat` event times in seconds.

Install the evaluation extra, then pass all eight held-out cache directories:

```bash
python -m pip install -e '.[evaluation]'
python experiments/evaluate_activations.py \
  --config config/casm-7f-default.json \
  --cache-dir caches/fold0_val \
  --cache-dir caches/fold1_val \
  --cache-dir caches/fold2_val \
  --cache-dir caches/fold3_val \
  --cache-dir caches/fold4_val \
  --cache-dir caches/fold5_val \
  --cache-dir caches/fold6_val \
  --cache-dir caches/fold7_val \
  --output-prefix results/my_backbone_8fold_7f
```

The evaluator trims the first five seconds, then uses `mir_eval` for F-measure (±70 ms), CMLt, and AMLt. It writes per-piece CSV and JSON aggregates. The Kaya batch script [`kaya/run_7f_cached_evaluation.sbatch`](kaya/run_7f_cached_evaluation.sbatch) records the exact cache layout used for the release refresh and reports missing cache families instead of silently producing partial tables.
