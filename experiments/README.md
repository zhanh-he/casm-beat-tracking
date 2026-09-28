# Experiments and paper evidence

This directory groups the paper-facing experimental record by decoder or
backbone. It separates runnable public artifacts from historical material and
does not claim reproducibility where a sealed source bundle is unavailable.

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
- [`DATA_AND_ANNOTATIONS.md`](DATA_AND_ANNOTATIONS.md): data, split, annotation,
  and preprocessing contract.

## Cached-activation format

The public CASM evaluator expects one `.npz` per piece with `piece`, `dataset`,
`has_downbeats`, 50 Hz `beat_logits` and `downbeat_logits`, and reference event
arrays `truth_beat` and `truth_downbeat`. See [`casm/README.md`](casm/README.md)
for the command-line entry point.
