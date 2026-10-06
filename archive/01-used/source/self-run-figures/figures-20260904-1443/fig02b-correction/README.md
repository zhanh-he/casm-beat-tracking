# Figure 2b correction receipt

This directory reproduces the corrected SMC 001/032 mechanism panel and the
two corresponding online-demo records. The correction changes only DBN.

## What was wrong

The superseded panel used the joint beat/downbeat
`DBNDownBeatTrackingProcessor` output for beat-only SMC material. Its dense DBN
path was therefore not a valid illustration of the standard beat-tracking DBN.
The Direct, CASM, and PLPDP arrays were not affected.

## What changed

- `redecode_fig02b.py` reads the exact frozen 50-fps Beat This out-of-fold beat
  probabilities already used by Direct and CASM.
- DBN is replayed with the beat-only `DBNBeatTrackingProcessor` through the
  archived `SequentialDBNDecoder`, using the matched 30–300 BPM range and its
  documented settings in `data/audit.json`.
- PLPDP is copied byte-for-byte from the original Figure 2b trace; it is not
  replayed or otherwise modified.
- `patch_fig02b_dbn_only.py` is the authoritative renderer for
  `fig02b-correct.png`: it retains the original PNG and replaces only the two
  DBN marker strips. `data/render_validation.json` verifies that the number of
  changed pixels outside those strips is zero.
- `plot_fig02b_corrected.py` is an independent source-level renderer for
  inspecting the same arrays; it is not used to replace the pixel-preserving
  paper PNG.
- `build_online_demo_cases.py` adds SMC 001/032 to either an `online-demo/` or
  `docs/` site tree and refreshes its embedded payload and integrity manifest.

The PLPDP path remains exactly as it appeared in the original Figure 2b. The
CASM candidate times, local periods, margins, and adaptive weights are likewise
the original arrays and plotting semantics.

## Reproduction

The decoder replay requires the frozen `auto-structbeat` environment and source
snapshot listed in `data/audit.json`. With that environment active:

```bash
python redecode_fig02b.py \
  --trace ../data/fig02_candidate_search_7f/traces/bt_smc_oof__smc__smc_001.npz \
  --trace ../data/fig02_candidate_search_7f/traces/bt_smc_oof__smc__smc_032.npz \
  --output-dir data

python patch_fig02b_dbn_only.py \
  --source-figure ../../../../figures/fig02b-wrong.png \
  --trace-dir ../data/fig02_candidate_search_7f/traces \
  --corrected-dir data \
  --output ../../../../figures/fig02b-correct.png \
  --receipt data/render_validation.json
```

The checked-in `data/audit.json` contains full-track and displayed-window
metrics plus SHA-256 hashes for both source and corrected trace archives.
`data/render_validation.json` is the separate pixel-level receipt.
