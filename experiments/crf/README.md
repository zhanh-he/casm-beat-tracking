# CRF baseline

The paper uses the released/default CRF beat-detection configuration on the
same frozen activation streams as the other post-processors. Downbeats are
decoded separately and snapped to the resulting beat grid.

No standalone CRF implementation or sealed piece-level output bundle is
redistributed here. The manuscript-level comparison is retained in
`../tables/`, while the historical research notes remain under `archive/`.
This distinction avoids presenting an incomplete artifact as independently
reproducible.
