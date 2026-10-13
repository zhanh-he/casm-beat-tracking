# MSCNN backbone

MSCNN is adapted to the shared 30-second, 50 Hz log-Mel input with unrelated
task heads removed. Decoder comparisons must reuse identical frozen MSCNN
activations for every post-processor.

The frozen-7F refresh status is documented in `../tables/RESULTS.md`.
Historical intermediate outputs remain on the `mirex_submission` research
branch and are not promoted as final release estimates.
