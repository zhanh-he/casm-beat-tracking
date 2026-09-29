# Evaluation eligibility — mandatory for every experiment

Before running inference or publishing a result, record for each checkpoint
its exact training-piece set, checkpoint-selection/validation-piece set,
decoder-calibration-piece set, and evaluation-piece set. Dataset names alone
are not enough when folds or duplicate recordings are possible.

**Hard stop:** A piece may not be counted as held-out *backbone* test evidence
if it was used for backbone training or checkpoint selection. A result cannot
be called fully held-out if it was used for decoder calibration either. Reject
unknown provenance. Cache reuse and pre-existing result files do not bypass
this check. Put exploratory backbone-in-sample diagnostics in a clearly
separate location, never in benchmark tables or figures.

For ICASSP SMC results, use out-of-fold backbone predictions and disclose the
frozen CASM 7F calibration protocol: folds 1–7 informed decoder selection,
so the eight-fold aggregate is **not** a fully held-out or nested decoder
estimate. Fold 0 and GTZAN were not used for that decoder selection. A final
model trained with SMC is **not** a held-out SMC backbone. For
the MIREX no-SMC protocol, only checkpoints with SMC excluded from all training
and selection can support held-out SMC diagnostics; SMC/GTZAN diagnostics must
not drive competition checkpoint selection. The sibling `mirex2026/` workspace
contains a machine-enforced manifest/piece-disjointness guard and a separate
no-SMC CASM configuration. Do not conflate it with the paper's 7F default.

Before each report, validate the checkpoint manifest against evaluation piece
IDs, then review every exported row/figure for provenance. A result-row
allowlist is a secondary safeguard, not a substitute for piece-level checking.
This policy applies
to all backbones and postprocessors, including Direct, DBN, CASM, CRF, and
PLPDP.
