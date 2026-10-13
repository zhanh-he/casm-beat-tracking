# MSCNN backbone

MSCNN is adapted to the shared 30-second, 50 Hz log-Mel input with unrelated
task heads removed. Decoder comparisons must reuse identical frozen MSCNN
activations for every post-processor.

The frozen-7F refresh status is documented in `../tables/RESULTS.md`.
Historical intermediate outputs remain in the
[`backup` archive](https://github.com/zhanh-he/casm-beat-tracking/tree/backup/archive/mirex-submission)
and are not promoted as final release estimates.
