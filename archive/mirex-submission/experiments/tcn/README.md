# TCN backbone

The TCN experiment uses the reimplementation adapted to the shared 30-second,
50 Hz log-Mel input, with the tempo task head removed. Decoder comparisons must
reuse identical frozen TCN activations for every post-processor.

The frozen-7F refresh status is documented in `../tables/RESULTS.md`; historical
intermediate outputs remain under `archive/` and are not promoted as final
release estimates.
