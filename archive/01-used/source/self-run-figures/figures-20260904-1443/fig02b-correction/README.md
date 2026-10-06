# Figure 2b correction receipt

This directory reproduces the corrected SMC 001/032 mechanism panel and the
two corresponding online-demo records.

## What was wrong

The superseded panel used the joint beat/downbeat
`DBNDownBeatTrackingProcessor` output for beat-only SMC material. Its dense DBN
path was therefore not a valid illustration of the standard beat-tracking DBN.
The Direct and CASM arrays were not affected.

## What was replayed

- `redecode_fig02b.py` reads the exact frozen 50-fps Beat This out-of-fold beat
  probabilities already used by Direct and CASM.
- DBN is replayed with the beat-only `DBNBeatTrackingProcessor` through the
  archived `SequentialDBNDecoder`, using the matched 30–300 BPM range and its
  documented settings in `data/audit.json`.
- PLPDP is replayed from the released `SunnyCYC/plpdp4beat` code at commit
  `30df4300849c843a7533e995113f4d26cd1e7d12f`, with its released 30–300 BPM
  limits and beat probability only. No per-track tuning is applied.
- `plot_fig02b_corrected.py` renders `fig02b-correct.png` from the audited
  corrected traces.
- `build_online_demo_cases.py` adds SMC 001/032 to either an `online-demo/` or
  `docs/` site tree and refreshes its embedded payload and integrity manifest.

The released PLPDP path remains dense on SMC 001. This is not a plotting error:
the decoder follows a faster competing subdivision in that track. Restricting
the tempo ceiling per track would improve the picture but would be post-hoc
tuning, so the corrected figure deliberately does not do that.

## Reproduction

The decoder replay requires the frozen `auto-structbeat` environment and source
snapshot listed in `data/audit.json`. With that environment active:

```bash
python redecode_fig02b.py \
  --trace ../data/fig02_candidate_search_7f/traces/bt_smc_oof__smc__smc_001.npz \
  --trace ../data/fig02_candidate_search_7f/traces/bt_smc_oof__smc__smc_032.npz \
  --output-dir data

python plot_fig02b_corrected.py \
  --data-dir data \
  --manifest ../data/fig02_candidate_search_7f/manifest.json \
  --output ../../../../figures/fig02b-correct.png
```

The checked-in `data/audit.json` contains full-track and displayed-window
metrics plus SHA-256 hashes for both source and corrected trace archives.
