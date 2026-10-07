# CASM systems for MIREX 2026 beat and downbeat tasks

This competition entry evaluates one frozen CASM postprocessor against two
madmom DBN tempo ranges on three separately trained backbones. It is not a
repeat submission of the ICASSP 2027 CASM methodology paper. BeatThis and the
shared 50 Hz log-Mel frontend are based on the upstream CPJKU Beat This code;
MSCNN is its lightweight multiscale CNN variant. TCN is the audited StructBeat
port using a fixed 128-to-74-band input adapter, not an upstream BeatThis
checkpoint. Each backbone emits both beat and downbeat logits. The task flag
controls which event times are written after decoding.

The exact packaged weights are train/validation-split checkpoints:

| Backbone | Allowed training pieces | Frozen checkpoint decision |
|---|---:|---|
| BeatThis | 3,783 | seed 2, zero-based epoch 119 |
| MSCNN | 3,783 | seed 0, zero-based epoch 1499 |
| TCN | 3,783 | seed 0, zero-based epoch 119 |

All use the BeatThis log-Mel pool. The remaining 556 allowed pieces were
reserved for validation; SMC and GTZAN were excluded from the entire
training/validation/model-selection/decoder-calibration process. The selection
rule used Direct beat and downbeat results on 27 annotated Beatles validation
pieces, weighting beat 60% and downbeat 40%, each with F/CMLt/AMLt weights
50%/25%/25%. These validation scores are development evidence, not official
MIREX test scores. The checkpoint hashes in `MANIFEST.json` disambiguate
these split weights from later full-allowed-data retrains.

CASM uses one globally frozen no-SMC 30–300 BPM configuration for every
backbone. DBN uses joint 3/4-meter inference at either 55–215 or 30–300 BPM.
Neither postprocessor trains or adapts on the input WAV. The executable
returns only event times; it performs no evaluation or access to annotations.
