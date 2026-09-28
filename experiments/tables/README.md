# Paper results

This directory is the single public home for paper-facing numerical results.

- `RESULTS.md`: validated release summary.
- `beat_this_8fold_7f_by_dataset.csv`: dataset-level locked results.
- `beat_this_smc_7f_by_fold.csv`: SMC fold-level results.
- `build_results_tables.py`: validates the compact source and rebuilds the
  public tables.
- `source/locked-7f/`: compact 4,556-piece source bundle.
- `ablation/`: final LaTeX ablation table and its supporting aggregate data.

Run from the repository root:

```bash
python experiments/tables/build_results_tables.py
```
