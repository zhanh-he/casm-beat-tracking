# ICASSP 2027 paper results

The CASM paper compares decoders on eight held-out backbone folds. Its
human-readable [result tables](tables/RESULTS.md),
[data/annotation protocol](DATA_AND_ANNOTATIONS.md), and selected
[figures](figures/) are retained here. BeatThis code and pretrained
architecture are from [CPJKU/beat_this](https://github.com/CPJKU/beat_this).

The separate MIREX checkpoint package uses different training restrictions.
An ICASSP fold-0 checkpoint is useful for testing the inference interface,
but it cannot alone reproduce an eight-fold aggregate or be scored on pieces
seen during its own training.

The [cached-activation evaluator](casm/evaluate_activations.py) reports
per-piece scores and aggregates by dataset and fold. It requires the original
activation caches and `pip install -e '.[evaluation]'`; those caches are not
included here. Fold numbers must be explicit in cache-directory names, and
pieces without downbeat annotations are excluded from downbeat averages.

## Backbones

Every decoder comparison uses identical frozen activations for all
post-processors.

| Backbone | Implementation and public results |
|---|---|
| BeatThis | Upstream [CPJKU/beat_this](https://github.com/CPJKU/beat_this) architecture and frontend. The locked evaluation covers 4,556 pieces over eight backbone-held-out partitions, including 217 beat-only SMC pieces. See [tables/](tables/). |
| MSCNN | Adapted to the shared 30-second, 50 Hz log-Mel input, with unrelated task heads removed. Frozen-7F refresh status is recorded in [RESULTS.md](tables/RESULTS.md). |
| TCN | Adapted to the shared 30-second, 50 Hz log-Mel input, with the tempo task head removed. Frozen-7F refresh status is recorded in [RESULTS.md](tables/RESULTS.md). |

The BeatThis architecture is upstream work; this paper studies CASM on top of
its activation streams. The MIREX no-SMC checkpoint must not replace an
ICASSP held-out fold checkpoint. Source audio and the complete training
environment are not distributed here.

Historical intermediate outputs and training materials remain in the
[`backup` archive](https://github.com/zhanh-he/casm-beat-tracking/tree/backup/archive/mirex-submission).
They are not promoted as final release estimates.
