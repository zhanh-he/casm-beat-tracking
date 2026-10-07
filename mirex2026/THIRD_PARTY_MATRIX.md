# Third-party and source provenance

- **Beat This!** architecture, frontend and inference helpers come from the
  CPJKU Beat This project. Its license is bundled at
  `third_party/beat_this/LICENSE`.
- **MSCNN** is the multiscale CNN adaptation in the same BeatThis fork; its
  implementation is bundled with that source. It is not an architecture
  contribution claimed by CASM.
- **TCN** model code in `mirex_pipeline/tcn_model.py` is the inference-only
  copy of the project's audited StructBeat TCN port. It uses the frozen
  checkpoint's 128-to-74-band adapter and does not require training code.
- **madmom** is installed from the pinned commit in `requirements-dbn.txt`.
- **PLPDP** reference `modules.py` is from
  [SunnyCYC/plpdp4beat](https://github.com/SunnyCYC/plpdp4beat), commit
  `30df4300849c843a7533e995113f4d26cd1e7d12` (MIT license included at
  `third_party/plpdp4beat/LICENSE`). `libfmp==1.3.0` is installed from
  `requirements-plpdp.txt`. The reference code assumes 100-fps activations;
  this package linearly resamples each 50-fps activation sequence to 100 fps,
  matching the project's ICASSP baseline adapter.

No BeatFM source, MERT weights, training audio, or annotations are present in
this archive. The package is for organizer-side inference, not a public
release of third-party training materials.
