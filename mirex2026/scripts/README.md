# MIREX evaluation scripts and eligibility rule

Run these scripts from an environment with the audited BeatThis and CASM
evaluation dependencies. They are experiment/diagnostic tools, **not** part
of the one-WAV MIREX submission runtime. The submission runtime lives in
`../mirex_pipeline/` and is packaged by `../build_submission.py`.

Every reported evaluation row must be checked against the checkpoint's
training provenance before inference and again before aggregation. A model
that trained on a dataset cannot be evaluated on that dataset as a comparison
or benchmark. Unknown provenance fails closed. For cross-validation, use the
exact train and evaluation piece inventories for each fold; the reported
out-of-fold score must use the checkpoint that held out each piece.

The official BeatThis `final0` checkpoint was trained on all available data
except GTZAN, including all SMC pieces. Therefore it is eligible for GTZAN
comparison here and ineligible for SMC. The `fold0` through `fold7`
checkpoints are separate models and can support an SMC out-of-fold analysis.

`evaluation_policy.py` enforces these facts for the current target diagnostic
runner. `run_target_comparison.sh` uses it before creating caches;
`report_target_comparison.py` rejects even preexisting raw rows from an
ineligible model and dataset pair. Do not bypass the guard by changing a
training-status label. Add new checkpoint provenance to the policy before
evaluating a new model family.

SMC and GTZAN remain diagnostics only for MIREX; neither panel is used for
checkpoint, seed, or decoder selection.

The corrected seed-0 baseline and its limits are in
[`../results/BASELINE_DIAGNOSTIC.md`](../results/BASELINE_DIAGNOSTIC.md).

`test_evaluation_policy.py` checks the model/dataset gate. New backbones
must add explicit checkpoint training provenance before any comparison run.
