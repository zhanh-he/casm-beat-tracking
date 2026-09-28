# CASM evaluation

`evaluate_activations.py` evaluates the frozen CASM decoder on cached 50 Hz
beat/downbeat activations. It trims the first five seconds and reports
`mir_eval` F-measure, CMLt, and AMLt.

```bash
python experiments/casm/evaluate_activations.py \
  --config casm/config/casm-7f-default.json \
  --cache-dir caches/fold0_val \
  --output-prefix experiments/tables/my_evaluation
```

The `kaya/` script records the eight-fold batch layout used for the release.
The locked public result source is in `../tables/source/locked-7f/`.
