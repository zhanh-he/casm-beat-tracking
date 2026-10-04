# BeatFM source audit and MIREX data gate

Status: **source inspected; the 911-piece verified-subset run completed and
passed independent inference smoke tests; its beat-tracking validation score
and checkpoint choice are pending. A separate 1,684-piece run is training.**

The user-supplied private archive is `~/Downloads/BeatFM.zip`, SHA-256
`4fbf554a78f2f353d1461f2267fa45f43b6cf864fc423f146ae46d301018858a`.
Its embedded `.git` directory does not resolve to a commit. The archive has no
README, license, requirements file, pretrained BeatFM checkpoint, or audio.
Keep it outside the public repository until redistribution rights are known.
The archive was copied, hash-checked, and unpacked in isolated directories on
Kaya (`/group/ems011/zhe/beatfm_mirex_20260930`) and Gadi
(`/scratch/wa66/hm6416/beatfm_mirex_20260930`).

## What the delivered code actually does

- `model.py` freezes MERT and trains the MSA, 1×1 convolution, and two
  classifiers. The viable MERT-95M constructor is `BeatFM("MERT95M")`;
  `train.py` and `test.py` default to `"MERT"`, which the constructor rejects.
- `dataset.py` loads `.npy` feature tensors, then the training loop passes them
  into the model as if they were raw waveform. `utils/save_features.py` has its
  `np.save` call commented out. Neither route is a valid end-to-end training
  pipeline as delivered.
- `config.py` assumes 16 kHz/50 Hz, while the pinned MERT-v1-95M model uses
  24 kHz and produces approximately 75 hidden-state frames/s. A 50 Hz output
  adapter and label-time alignment must be tested before scoring.
- The default dataset list contains SMC and the default training loop runs
  eight folds; neither is the MIREX no-SMC single-model protocol.
- `val_epoch` does not enter eval mode and its loss scheduler is configured to
  maximize loss, then stepped a second time with epoch number. This invalidates
  its checkpoint-selection logic.
- The [BeatFM paper](https://arxiv.org/pdf/2508.09790) describes 15-second
  clips with 5-second overlap, Adam at 3e-4, batch size 16 and patience 20.
  The delivered code uses 30-second random crops, Adam at 1e-3, batch size 24,
  and a different early-stop rule. It also has five MSA dilations and additive
  branch fusion, whereas the paper describes four dilations and multiplicative
  fusion. We will label any run by the actual source architecture and recipe,
  not present it as an exact paper reproduction.

The 5090 synthetic-waveform inference smoke test instantiated the MERT95M
source model with pinned MERT revision
`12af15fef9d0ac838c3f475bfbbf26d2060dd4f5` and returned finite beat
and downbeat logits. **It did not test a trained checkpoint or real audio.**
The same MERT snapshot has been staged privately on Kaya and Gadi;
Kaya's `pytorch_model.bin` SHA-256 is
`a2b8b747f72c06e0595aeae41ae5473f4364938c6b39b2c58be38c48e6bd3fcd`.
Both clusters have isolated Transformers 4.45.1/THOP dependency directories,
without mutating the existing BeatThis Python environments.
The private source head plus pinned MERT loaded successfully in CPU smoke
tests on both clusters; Kaya's one-second synthetic forward returned twelve
encoder layers and finite `(1, 1, 74)` beat/downbeat logits. MERT's own
convolution-length method confirms 1,124 output frames for the proposed
15-second training clip. These are shape checks, not performance results.
For cluster smoke testing, the private extracted source had only its two
unused `matplotlib`/`numpy` imports removed from
`MultilevelSemanticAggregation.py`. The patched
file SHA-256 is
`b9b864d7e05daad9336b827af13e41e73b29b55dbd8fd646d2c47dfa57413129`;
the archive's original file SHA-256 is
`c8e2aeec407b1241491904bc8d642ff0e9fb93cfd50ac652b5a3128d2464fa22`.
This does not change model calculations.

## MIREX protocol and current blocker

The [2026 MIREX beat-tracking rules](https://music-ir.org/mirex/wiki/2026:Audio_Beat_Tracking)
prohibit **all** SMC and GTZAN splits from training, validation, model selection,
parameter tuning, or any other development use. Prior SMC/GTZAN observations
must not guide the submitted BeatFM experiment. The BeatFM paper's SMC result
is from eight-fold cross-validation with SMC training folds; it is not a
no-SMC score.

Run [`beatfm_manifest.py`](beatfm_manifest.py) against BeatThis's
`data/annotations` tree. It uses the official `single.split` files, excludes
SMC and GTZAN from supervised development, and rejects missing original audio.
On Kaya the split/annotation hash is
`8fdf988994f779ac118ca0e6abd8823e581c57208729ebb787dc68c3dacd0682`:
3,783 train pieces and 556 allowed-validation pieces; one Beatles piece has an
empty beat annotation. A few Harmonix annotations start just before zero;
training targets must clip those events to the waveform support.

The Kaya BeatThis data view has spectrogram caches, not waveforms. No matching
original audio for the 4,339-piece pool was found *in that cache*. Separate
raw-audio collections exist on 5090, but no complete source location has been
established. The [RWC 2.0 audio release](https://zenodo.org/records/18656623)
contains Popular (used in the BeatFM paper) and the other RWC subsets in the
BeatThis split. All four collection archives have been acquired on Kaya,
verified against the release MD5s, and mapped to the legacy stems:

| Collection | WAVs | Published MD5 | Aligned map SHA-256 |
| --- | ---: | --- | --- |
| Popular | 100 | `960a11a2d7fb603ad0dae8428f53d4f0` | `53784a9dbc11e5b0682870cf10f84b05ead7fe893c00df5ebdd9e360e649db40` |
| Classical | 61 | `2ac9139c4f03a65885ae0d0d299f67f8` | `52f87ee809b2b829f1248903c36f65b5414d42e2f66841e0e0d06cccbb65d331` |
| Jazz | 50 | `c5d7d989e1afb8257ec50a3696d90c37` | `88ae9c2204cdff8e77326ad1d3d986d4cdf0a1d0d9461f6f29ae1d91d47434a8` |
| Royalty-free | 15 | `63e3b6263656a42c592ce1e90a88caa3` | `0d6e98f8c9bff198f8356fd80d3da476f32caffcb1f275a2c403e74fd38cd0ef` |

The
[RWC annotations metadata](https://github.com/rwc-music/rwc-annotations)
provides legacy CD and track numbers to map `RWC_Pxxx.wav` to BeatThis stems.
The metadata/annotation checkout on Kaya is pinned at commit
`0a1a6c31dbe73a7f5d44f7caef8cd0999402a4c2`.
[`rwc2_audio_map.py`](rwc2_audio_map.py) checked CD/track identities, WAV
durations and full-song beat-time alignment for all 226 recordings.
Two tracks have a total of three *beat-in-bar* label corrections in the RWC
2.0 annotation, so the mapper reports these differences while retaining the
BeatThis labels in Royalty-free. In 26 Jazz tracks BeatThis uses half the beat density of the
new RWC annotation, so raw beat-count equality would have falsely rejected
the correct recording. The mapper retains the BeatThis metrical level and
reports 17 beat-in-bar label differences across three Jazz tracks. Three
Popular recordings need a constant release-time offset applied to the
BeatThis annotation (`CD2_14`: -0.218 s, `CD3_06`: -0.029 s,
`CD3_11`: -0.012 s); two others have isolated local beat corrections. These
differences are recorded, not silently hidden. Any beats beyond WAV support
are clipped when targets are built.
The original [Ballroom archive](https://github.com/CPJKU/BallroomAnnotations)
was also obtained on Kaya with the published MD5
`2872a3e52070bc342a4510a95e2fa0b8`. It contains 698 WAVs;
[`ballroom_audio_map.py`](ballroom_audio_map.py) mapped all 685 pieces in the
BeatThis split with no exact cross-split duplicate WAVs. Its verified map
SHA-256 is `0d199ff9dd9bfdcf1eab871b4fb4b0b038a22045605fb3ec6bd86e84063ee9f4`.
The Ballroom source documents four exact and nine recording-replica pairs.
The mapper also checked those 13 published pairs against the BeatThis split:
none straddles train/validation among the 685 included tracks. This is not
a general acoustic-near-duplicate search, so the validation set should not
yet be presented as exhaustively de-duplicated.
One Ballroom track has its last labeled beat 0.13 seconds beyond the recording
and requires waveform-boundary clipping. The first **911**-piece verified
subset (685 Ballroom + 226 RWC) was frozen before acquiring Hainsworth;
do not silently rewrite its manifest or running job.

The [Beat Transformer authors' data guide](https://github.com/zhaojw1998/Beat-Transformer#audio-data)
links a research mirror of the Hainsworth WAVs. The 956 MB archive was fetched
privately on 5090, transferred to Kaya, verified as a complete tar archive,
and SHA-256-checked on both hosts:
`e6d79b48d467c238b98d29af356fe6cc26d61ea072bf30f18e8f2677c5de5b71`.
It contains **222** WAVs, with exactly the same 222 IDs as the BeatThis split.
[`hainsworth_audio_map.py`](hainsworth_audio_map.py) checked every WAV header,
annotation interval, and exact cross-split duplicate; all 222 passed with
zero boundary-label clips. Its Kaya map SHA-256 is
`68259bf06564a870d02791d921ea911feb361f75e5fce899d73c8ae2bde90d92`.
All 222 original WAV durations match the released BeatThis spectrograms to
within 0.020 seconds; one paired 15-second excerpt has a cached-versus-recomputed
log-Mel MAE of 0.0213. This raises the verified original-waveform pool to
**1,133** pieces (963 train, 170 allowed validation), but no 1,133-piece
training run or BeatFM score has been claimed. The mirror is third-party;
retain it privately and do not redistribute audio without rights review.

Further allowed-data acquisition (all separate from the frozen 911-piece run):

- The [official Candombe archive](https://www.eumus.edu.uy/candombe/datasets/ISMIR2015/)
  was fetched privately on Kaya, SHA-256
  `05ffa89892e0566035cc4089b731bfdd40d47c3108afa4fdf34bb15880a2eb89`.
  [`exact_stem_audio_map.py`](exact_stem_audio_map.py) verified all **35**
  FLACs against the BeatThis IDs, beat intervals, and cache durations (max
  absolute difference 0.020 s), with no cross-split exact duplicate. Map hash:
  `59d335302ae70fb6646dc8f8524e288f7f1f711676b5a073cf12d632f27b2306`.
- The [official Groove v1.0.0 archive](https://magenta.tensorflow.org/datasets/groove)
  was fetched privately on Kaya and matches its published SHA-256
  `21559feb2f1c96ca53988fd4d7060b1f2afe1d854fb2a8dcea5ff95cf3cce7e9`.
  [`groove_audio_map.py`](groove_audio_map.py) matched all **336** BeatThis
  stems to the source WAVs and cached durations (max difference 0.020 s),
  with no cross-split exact duplicate. Map hash:
  `e419b94e7ffe49484dccfd7cd9fed5b5aed211bb9d6dd9e0ba47b6731be32002`.
  **Annotation defect:** 48 tracks have beats past their actual audio end;
  30 overrun by more than 1 s, 21 by more than 30 s, and four affected
  tracks are in the allowed validation split. The worst overhang is 273.93 s.
  The waveform and BeatThis spectrogram have the same length, so this is a
  label-boundary issue, not a source-audio mismatch. Clip out-of-range labels
  when building targets and explicitly handle these four validation tracks;
  do not silently count all 336 as pristine supervision.
- The [official GuitarSet mono pickup-mix archive](https://zenodo.org/records/3371780)
  was fetched privately on Kaya and matches the published MD5
  `aecce79f425a44e2055e46f680e10f6a`. It contains 360 WAVs; the BeatThis
  split selects **180**. [`exact_stem_audio_map.py`](exact_stem_audio_map.py)
  verified all 180 identities, annotation bounds, and cache durations (max
  difference 0.020 s), with no exact cross-split duplicate. Map SHA-256:
  `7ead3d5e944587101bcfe2e0df847bb5663967e9c6588a903a2e8bfafb534e94`.

Thus **1,684** allowed pieces now have source-audio ID and duration mappings
(Ballroom 685, RWC 226, Hainsworth 222, Candombe 35, Groove 336,
GuitarSet 180): 1,431 train and 253 allowed validation. The Groove annotation
caveat remains. The separate Kaya run `69061` is in progress; no completed
1,684-piece BeatFM training result is claimed.

The [LabROSA chord-recognition source page](https://www.ee.columbia.edu/~dpwe/LabROSA/projects/chords/)
also provides a 2009 Beatles archive: 180 mono MP3s at 32 kbps/16 kHz, not
BeatThis's original recording release. The private Kaya ZIP passes `unzip -tq`
and has SHA-256
`8ea52011afefe958ec98b06a077475f37d15f4d1bcbeea6ef69c7c389b244ec1`.
[`beatles_labrosa_index.py`](beatles_labrosa_index.py) maps all 180 by album
and track number, but intentionally emits an **alignment-unverified** index,
not a training audio map. On the first track, candidate duration is 177.336 s
versus 175.820 s in BeatThis; a 0.56 s offset improves first-40-second
low-band log-Mel temporal correlation only from 0.057 to 0.516. The first
15-second cached-versus-aligned-source log-Mel MAE is still 1.366, far above
the Hainsworth paired-WAV value. Different edition/encoding/time alignment
must be resolved track by track before these MP3s can supervise BeatFM.

BeatThis's released 128-bin log-Mel is **not** a direct input to the released
MERT-v1-95M waveform encoder, but it *can* be inverted to approximate audio.
The Beat Transformer authors [document inverse-Mel plus Griffin–Lim for
Harmonix](https://github.com/zhaojw1998/Beat-Transformer#audio-data).
[`probe_beatthis_mel_inversion.py`](probe_beatthis_mel_inversion.py) applied
the exact BeatThis scaling to paired allowed-set Ballroom and Hainsworth
excerpts. Their reconstructed-versus-cached log-Mel MAEs are 0.0394 and
0.0399; mean cosine between frozen MERT's final hidden states for original
and reconstructed 15-second audio is 0.726 and 0.742, respectively. These
show a technically viable *synthetic-audio* path, not equivalent waveform
quality, beat-tracking accuracy, or a paper-identical BeatFM result. No
SMC/GTZAN data were used in these probes. A candidate BeatFM checkpoint must
be compared on the allowed validation split before synthetic Beatles/Harmonix
audio is promoted into training. Keep original and reconstructed provenance
separate.
An explicit 700-piece **pilot-only** manifest was generated on Kaya, with
596 train and 104 allowed-validation pieces, SHA-256
`2080360216c7648d56ac41a9216bf7a8364e26cf69133e3d8df1eefe12e70809`.
The expanded verified 911-piece manifest has 774 train and 137 validation
pieces, SHA-256
`24deea630d5c7d8bf88f4f1d9c035c3370ae3a5ff181d448e5a164a9f5e13f1b`;
three Popular annotation offsets are carried explicitly. Both manifests are
subset-only, not full-pool manifests.
The regular manifest builder still rejects partial audio by default; the
pilot requires `--pilot-partial-audio` at both manifest and training stages,
and embeds `pilot_partial_audio_not_submission` in checkpoint provenance.
Kaya SLURM job `45557` failed **before training** because its submitted
`--source-dir` pointed one level above `BeatFM/`; the failed run directory was
preserved. The corrected one-epoch smoke run, job `45587`, completed with exit
0 in a distinct `retry1` directory (700 one-crop-per-song pieces, training
loss 0.7109, validation loss 0.6337). Its checkpoint SHA-256 is
`ac061b38c3880c514ea3367b75ae9014b8df7ea985485b3ca9fdfac6592ab3bb`.
These losses are engineering signals, not beat-tracking metrics. Neither job
is a paper reproduction, model-selection run, or submission candidate.
The 911-piece full sliding-clip verified-subset job `45647` completed on
Kaya, with a fresh run directory, effective batch 16 and
100-epoch ceiling/20-epoch early-stop (22 actual epochs). Its split manifest SHA-256 is
`24deea630d5c7d8bf88f4f1d9c035c3370ae3a5ff181d448e5a164a9f5e13f1b`.
This is a reduced-data MIREX candidate, not an equal-data BeatThis comparison
or a published BeatFM reproduction. Its best validation-loss checkpoint is
epoch 2 (SHA-256
`174c4b056b47e344eb841de5f6025581cd8e7f2362a5aafb99a7d3bfe63892cb`),
but this is **not** a beat-tracking metric or the frozen MIREX choice.
Five epoch candidates were scored on all 137 allowed Ballroom/RWC recordings
on lab5090 (inference only). The predeclared Direct beat composite selected
epoch 15 (SHA-256
`44a1a33f6c3d08180bea2f0619c16a39a756644f101d0cd5d1691f7abd8ba764`);
the [raw results and caveats](../results/beatfm/README.md) are retained.
Failed Kaya launchers `69059`/`69065` produced no scores, and queued
duplicate `69069` was cancelled before starting. Job `69066` will run a
matched-panel evaluation after the 1,684-piece training completes.
The separate inference adapter was also smoke-tested on lab5090, which did
**no training**: loading the pilot head and pinned MERT, it processed a real
Ballroom WAV (`Media-104108.wav`) into 1,590 finite beat/downbeat-logit
frames at 50 Hz. That 31.8-second forward pass establishes wiring, not
accuracy. The pilot checkpoint requires an explicit smoke-only environment
override; an ordinary submission path refuses it.
For the eventual complete manifest, `train_beatfm.py` now indexes 15-second
clips every 10 seconds (5-second overlap) at the piece-disjoint split, loads
only the source-audio interval needed per clip, and supports gradient
accumulation to retain an effective batch of 16 on smaller GPUs. A CPU data
smoke on one verified RWC-R recording yielded 13 clips with 360,000 waveform
samples and aligned `(2, 1124)` targets each. This tests data shapes, not
training quality or whole-song validation metrics.

The [BeatThis data README](https://github.com/CPJKU/beat_this/blob/main/README.md)
publishes annotations and spectrograms, not the raw waveforms required by
MERT. The [BeatThis-MDM repository](https://github.com/fosfrancesco/md_beat_this)
publishes predictions/logits, not a replacement raw-audio corpus.
[Isophonics Beatles](https://isophonics.net/content/reference-annotations.html)
identifies the exact CDs used for its annotations but does not distribute
the recordings; the [Harmonix Set](https://github.com/urinieto/harmonixset)
provides labels, mel spectrograms, and third-party video URLs/alignment code,
not the original 912 waveforms. Substituting a different master or video
without a validated time alignment would corrupt training labels.
An [open Harmonix issue](https://github.com/urinieto/harmonixset/issues/18)
confirms that researchers still cannot obtain the exact original audio from
the repository and are asking which commercial copies match. The published
YouTube alignment notebook is a possible *different-source* research path,
not proof of identical recordings or redistribution rights.
To make that option inspectable without *bulk* downloading copyrighted recordings,
[`harmonix_source_index.py`](harmonix_source_index.py) joined all 911 BeatThis
Harmonix IDs to the official label files, video URLs, and published alignment
scores by numeric ID (some track-name suffixes differ). The private Kaya
metadata-only index has SHA-256
`1c2fa246d9e5b7b114455193c8079ff51a5aeb959945573282851968c57195cc`;
the official metadata checkout is commit
`64abeb509429e73d74559fb98e621dac866efea1`. Scores have median 0.9840,
but 37 of 911 are below 0.9. These scores do not turn the URLs into verified
original audio, and no Harmonix WAV is present in the training manifest.
As a controlled private feasibility check, the officially indexed video for
`0001_12step` was available and its audio was fetched; the published alignment
score is 0.9984. The video audio lasts 204.43 s whereas BeatThis's included
spectrogram lasts 138.78 s. The first 40 s of low-band spectrogram has temporal
correlation 0.102 at zero lag and 0.955 at a 1.34 s shift, showing that this
*particular* public source could potentially be aligned. It is still a
different, longer video version; neither its full-track alignment nor its
rights for bulk acquisition/redistribution are established. No broad video
download or Harmonix training manifest has been launched.
BeatThis spectrograms cannot be passed directly to MERT. They can be inverted
to *synthetic* audio, but the discarded phase and spectrum detail cannot be
restored or called the original recording; the paired-audio probe above is
only an input-feasibility check. **No full-BeatThis-pool BeatFM training job
should start until the
4,339-piece raw-audio manifest passes with zero missing files.** A separately
declared **verified-subset** MIREX candidate can be valid if it trains only on
the aligned, allowed pieces and selects only on its disjoint allowed
validation split. The running 911-piece job remains frozen; the 1,133-piece
Hainsworth-extended subset must be a distinct run if pursued. Neither is the
same-data controlled comparison to
BeatThis, and the data difference must be disclosed. The one-epoch engineering
pilot above is not itself a submission candidate or performance result.

Once the audio is located, train on the allowed train split and choose
seed/epoch/decoder with allowed validation only. Freeze the choice and retrain
on all allowed pieces, then package Direct, CASM 30–300, DBN 55–215, and
exploratory DBN 30–300. Do not run SMC or GTZAN development diagnostics for
the submitted system. This excludes SMC and GTZAN from *supervised fine-tuning*;
overlap with MERT pretraining has not been established and must not be claimed
absent.
