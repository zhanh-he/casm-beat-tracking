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
