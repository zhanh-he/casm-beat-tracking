# Beat This backbone

Beat This supplies the primary frozen activation streams. The public locked
evaluation covers 4,556 pieces across eight backbone-held-out partitions; SMC
is the 217-piece beat-only subset. The compact source bundle and regenerated
tables are in `../tables/`.

The BeatThis backbone code is taken directly from the public
[CPJKU/beat_this repository](https://github.com/CPJKU/beat_this), including
its model and preprocessing recipe. We did not design or claim the BeatThis
architecture; the paper studies CASM on top of its eight-fold activations.
This repository distributes CASM and result metadata, not source audio or a
complete sealed copy of the upstream training environment. Do not substitute
the MIREX no-SMC checkpoint for an ICASSP held-out fold checkpoint.
