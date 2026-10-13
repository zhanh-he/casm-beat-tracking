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
