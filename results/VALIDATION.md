# Result-table validation

Status: **PASS**

- Locked completion marker present.
- Candidate hash: `93f40ad87602ae68d84c6d1d72e307c27a67cc94d2b508f619f3376df08ae7de`.
- Protocol hash: `9b9e84109178a998f9c9215244c7eee2be1b4d1c1bf4b25d93147c462668fae3`.
- Default JSON parameters exactly match the locked selection and result summary.
- Coverage: 4556 unique pieces, 18 datasets, folds 0–7.
- Metric ranges: every finite value lies in [0, 1].
- Downbeat coverage: 3744 pieces; missing values occur only for Simac and SMC, consistently across all three downbeat metrics.
- Recomputed overall, SMC, and per-fold macro metrics match `summary.json` to absolute tolerance `1e-12`.
- Locked evaluation runtime recorded by the source bundle: 11.551 seconds.

Run `python scripts/build_results_tables.py` from any directory to repeat validation and regenerate the public CSV/Markdown tables. This validator does not train a model or access a cluster.
