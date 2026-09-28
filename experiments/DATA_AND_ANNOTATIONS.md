# Data and annotation provenance

CASM does not redistribute audio. The experiments use the data layout, annotations, spectrogram recipe, and eight-fold splits released with [Beat This!](https://github.com/CPJKU/beat_this).

## Annotations and splits

The local experimental copy is an exact content match to [`beat_this_annotations` v1.0](https://github.com/CPJKU/beat_this_annotations/releases/tag/v1.0): on 2026-09-21 we compared the relative path and SHA-256 of all 5,605 files, with zero missing, extra, or changed files. This matters because v1.1 corrects eight annotation files; the reported experiments intentionally retain v1.0 for paper reproducibility.

Each dataset contains `.beats` files and Beat This's `8-folds.split`. A two-column annotation stores time in seconds and beat number, with beat number 1 denoting a downbeat. Datasets without downbeat annotations store beat times only; consequently SMC and Simac have no downbeat scores. For fold `k`, Beat This uses split part `k` for validation and the other seven parts for training. GTZAN is excluded from this cross-validation pool and used as a separate held-out test set.

The upstream annotation repository documents the original dataset-specific sources and corrections. Users must cite and follow the terms of the underlying audio datasets as well as Beat This; the annotation license does not grant rights to the audio.

## Spectrogram generation

We use the Beat This preprocessing code and released spectrogram layout, not a separately designed CASM frontend:

1. Load audio, mix multichannel input to mono, and resample to 22,050 Hz.
2. Compute a 128-bin Mel spectrogram with a 1,024-sample FFT, 441-sample hop (50 frames/s), 30--11,000 Hz range, Slaney Mel scale, `frame_length` normalization, and magnitude (`power=1`).
3. Apply `log(1 + 1000 * magnitude)` and store the result as `float16` NumPy arrays, either individual `.npy` files or uncompressed arrays inside a memory-mappable `.npz` bundle.

The stored spectrogram represents the full track. During training, Beat This samples 1,500-frame (30-second) excerpts. Its default training augmentation uses pitch shifts from -5 through +6 semitones and tempo changes from -20% through +20% in 4% steps; validation and test evaluation use unaugmented full pieces. CASM itself receives only the resulting 50 Hz beat and downbeat logits and does not read audio or spectrograms.

The exact upstream implementation is in `beat_this/preprocessing.py`, `launch_scripts/preprocess_audio.py`, and `beat_this/dataset/dataset.py` in the Beat This repository.
