# Release checklist

- [x] Freeze 7F as the package and CLI default.
- [x] Record candidate/protocol hashes and all scalar parameters.
- [x] Provide API, CLI, tests, benchmark, and cache evaluator.
- [x] Check the package decoder event-for-event against the sealed implementation.
- [x] Add callable beat/downbeat processors and package-data defaults.
- [x] Build-check the wheel and source distribution in CI.
- [x] Document Beat This annotation/spectrogram provenance.
- [x] Inventory recoverable checkpoint files by SHA-256.
- [x] Validate and publish the locked Beat This 7F per-dataset and SMC fold tables.
- [ ] Rerun `final0`--`final2` with frozen 7F and report GTZAN mean ± sample SD.
- [ ] Choose and add a license for CASM code and CASM-trained weights.
- [ ] Claim `casm-beat-tracking` on TestPyPI/PyPI and configure Trusted Publishing.
- [ ] Recover or retrain missing TCN `final2` and fold0--fold7 checkpoints.
- [ ] Recreate the purged MSCNN eight-fold activation cache and rerun 7F.
- [ ] Publish model cards and weights; replace manifest statuses with public URLs.
- [ ] Tag the reviewed release and archive it with Zenodo.
