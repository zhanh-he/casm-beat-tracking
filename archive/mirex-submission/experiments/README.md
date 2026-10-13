# Experiments and paper evidence

This directory groups the paper-facing experimental record by decoder or
backbone. It separates runnable public artifacts from historical material and
does not claim reproducibility where a sealed source bundle is unavailable.

This is the **ICASSP 2027 paper** workspace on `paper-revision`. The BeatThis
backbone architecture, training/preprocessing implementation, and starting
code come directly from the upstream [Beat This repository](https://github.com/CPJKU/beat_this);
BeatThis is not our proposed neural architecture. Our paper contribution is
CASM postprocessing and its controlled comparisons on the paper's eight-fold
protocol. The backbone source/checkpoint packaging limits are recorded below.

The sibling [`mirex2026/`](../mirex2026/) directory is a competition system,
not a second copy of this submission. It excludes SMC and GTZAN from
backbone development and uses a final full-data retrain on the remaining
allowed pool. Its checkpoints must not be mixed with these eight-fold results.

All benchmark rows must pass the [evaluation eligibility policy](../EXPERIMENT_EVALUATION_POLICY.md).

## Decoders

- [`casm/`](casm/): frozen CASM evaluator and eight-fold batch entry point.
- [`dbn/`](dbn/): DBN calibration-scale driver, frozen protocols, audits, and
  fixed-panel summaries.
- [`crf/`](crf/): exact baseline usage and artifact-availability note.
- [`plpdp/`](plpdp/): exact baseline usage and result pointers.

## Activation backbones

- [`beat_this/`](beat_this/): primary locked eight-fold evaluation.
- [`tcn/`](tcn/): TCN adaptation and frozen-7F refresh status.
- [`mscnn/`](mscnn/): MSCNN adaptation and frozen-7F refresh status.

## Paper outputs

- [`tables/`](tables/): validated tables, compact locked source, and ablation
  artifacts.
- [`figures/`](figures/): the three final paper figures retained in this repo.
- [`../archive/`](../archive/): copies of selected figures and separate
  historical/unselected figure outputs with source snapshots.
- [`DATA_AND_ANNOTATIONS.md`](DATA_AND_ANNOTATIONS.md): data, split, annotation,
  and preprocessing contract.

## Cached-activation format

The public CASM evaluator expects one `.npz` per piece with `piece`, `dataset`,
`has_downbeats`, 50 Hz `beat_logits` and `downbeat_logits`, and reference event
arrays `truth_beat` and `truth_downbeat`. See [`casm/README.md`](casm/README.md)
for the command-line entry point.

## Source-bundle status

The CASM cached-activation evaluator, eight-fold batch entry point, DBN
calibration driver, result validator, figures, and compact locked result source
are present here. The BeatThis, MSCNN, and TCN directories currently
preserve their protocols and result pointers; their complete cluster training
source snapshots and weight files are not yet sealed here. Those directories
are the reserved import locations, and no README-only entry is represented as
a runnable training implementation.
