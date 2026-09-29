# CASM ablation artifacts

This directory preserves the BeatThis ablation result used in the manuscript.

- `casm_ablation_table.tex`: final table source used by the paper.
- `aggregate_metrics.csv`: GTZAN and SMC backbone-out-of-fold aggregate values supporting the table. The SMC 7F CASM aggregate is not fully held-out with respect to decoder calibration; see `casm/docs/CALIBRATION.md`.

The earlier `tcn_smc_final0` panel and `fig03a.*` visualization were removed:
that TCN final checkpoint was trained with SMC and then evaluated on the same
217 SMC pieces. Those values were in-sample and are not benchmark evidence.
The source history retains provenance, but the active results must not reuse
them. See the root evaluation policy and run the aggregate row allowlist
validator after edits; it does not prove piece-level training disjointness.
