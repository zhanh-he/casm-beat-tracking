# The same 137 allowed pieces across BeatThis, MSCNN, and BeatFM

The report script reconciled **the exact 103 Ballroom and 34 RWC piece IDs**
across all three backbones and all four decoders, rejecting duplicate,
missing, target-dataset, or non-finite rows. Values are piece-macro beat
percentages on allowed development data, **not MIREX test scores**.

| Backbone / checkpoint role | Decoder | Beat F | CMLt | AMLt |
|---|---|---:|---:|---:|
| BeatThis search | Direct | 94.74 | 89.62 | 92.36 |
| BeatThis search | CASM | **94.84** | **90.10** | 93.11 |
| BeatThis search | DBN 55–215 | 94.36 | 90.02 | **93.68** |
| BeatThis search | DBN 30–300 | 94.36 | 89.65 | 93.32 |
| MSCNN train-split | Direct | 91.62 | 82.67 | 85.10 |
| MSCNN train-split | CASM | **91.88** | 83.42 | 86.08 |
| MSCNN train-split | DBN 55–215 | 91.10 | **84.61** | **89.51** |
| MSCNN train-split | DBN 30–300 | 90.62 | 83.94 | 88.50 |
| BeatFM 911-piece train-split | Direct | 82.89 | 62.00 | 68.18 |
| BeatFM 911-piece train-split | CASM | **83.98** | 65.88 | 71.96 |
| BeatFM 911-piece train-split | DBN 55–215 | 82.54 | **70.38** | 82.02 |
| BeatFM 911-piece train-split | DBN 30–300 | 81.95 | 68.88 | **84.96** |

Under this panel, CASM raises beat F relative to Direct by 0.10, 0.26, and
1.09 percentage points for BeatThis, MSCNN, and BeatFM respectively. It also
raises CMLt and AMLt for each. Default DBN has higher AMLt than CASM for all
three, but lower beat F; the particularly large BeatFM/RWC DBN drop is visible
in the [BeatFM per-dataset table](../beatfm/README.md). These are observed
development-set differences, not a claim of out-of-sample advantage.

Crucial scope differences: BeatThis is the held-out **search checkpoint**
selected on allowed Beatles pieces; its final 120-epoch model was subsequently
retrained on all 4,339 allowed pieces and cannot be independently evaluated
on this former validation panel. MSCNN uses its selected train-split seed-0
last checkpoint. BeatFM uses its allowed-validation-selected epoch-15 weight,
trained on only 774 of the 911 available Ballroom/RWC subset pieces. The
BeatFM raw WAVs and three explicitly documented RWC annotation-time shifts
also differ from BeatThis/MSCNN's cached-spectrogram input representation;
the piece IDs and split are identical, not necessarily the audio mastering.
This table is therefore a **matched-piece development comparison**, not an
equal-data architecture ranking.

The auditable [36-row summary](summary.csv) includes `all`, `ballroom`, and
`rwc` per decoder, with downbeat metrics; [provenance](provenance.json) records
every source CSV SHA-256. The reconstruction command is:

```sh
python mirex2026/scripts/report_common_allowed_matrix.py \
  --beatthis-dir mirex2026/results/beatthis_seed2_allowed_panel_20261004 \
  --mscnn-dir mirex2026/results/mscnn_seed0_allowed_screen_20261004/last_1499 \
  --beatfm-dir mirex2026/results/beatfm/allowed_eval_911_5090_20261004 \
  --output-dir /new/output/directory
```

No SMC or GTZAN result was used for this report. The frozen CASM configuration
was calibrated on the broader allowed validation pool that contains these
137 recordings, so its values are system-development evidence rather than an
unbiased test of decoder generalization.
