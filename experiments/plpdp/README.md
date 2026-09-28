# PLPDP baseline

PLPDP is evaluated with its released/default configuration on the same frozen
activation streams used by Direct, CASM, and DBN. For streams without a joint
beat/downbeat decoder, downbeat estimates are decoded separately and snapped to
the selected beat grid.

Aggregate PLPDP comparisons are included in
`../tables/ablation/aggregate_metrics.csv`. Historical piece-level exports and
figure-generation inputs are retained under `archive/`.
