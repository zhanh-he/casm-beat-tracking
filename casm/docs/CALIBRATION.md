# CASM 7F calibration

The release default is the single CASM configuration selected on the union of SMC folds 1--7 ("7F"). Fold 0 did not enter decoder selection. The selected configuration was then frozen across tracks, datasets, and backbones; CASM does not estimate parameters per track and has no learned weights or random seed.

The machine-readable default is [`config/casm-7f-default.json`](../config/casm-7f-default.json). Its candidate hash is `93f40ad87602ae68d84c6d1d72e307c27a67cc94d2b508f619f3376df08ae7de`; the locked protocol hash is `9b9e84109178a998f9c9215244c7eee2be1b4d1c1bf4b25d93147c462668fae3`.

## Default parameters

| Parameter | Default | Meaning |
| --- | ---: | --- |
| `fps` | 50 | Activation frame rate |
| `candidate_threshold` | 0.03 | Minimum beat probability for a path candidate |
| `min_bpm`, `max_bpm` | 30, 300 | Allowed local inter-beat interval support |
| `local_window_seconds` | 8 | Local autocorrelation window |
| `tempo_bias` | 0.15 | Mild preference against longer lag hypotheses |
| `temperature` | 2 | Beat-logit temperature |
| `logit_clip` | 6 | Observation-score clipping |
| `duration_weight` | 4 | Maximum duration-potential strength |
| `duration_sigma` | 0.15 | Duration tolerance under confident periodicity |
| `uncertain_sigma` | 0.4 | Additional tolerance under ambiguous periodicity |
| `fallback_minimal_ratio` | 0.85 | Fall back if the CASM path is too sparse vs. direct |
| `fallback_maximal_ratio` | 1.8 | Fall back if the CASM path is too dense vs. direct |
| `downbeat_mode` | `meter` | Beat-synchronous meter decoding |
| `meters` | 2, 3, 4, 5, 6, 7 | Candidate beats per bar |
| `meter_change_penalty` | 3 | Penalty for changing meter along the path |
| `downbeat_temperature` | 4 | Downbeat-logit temperature |
| `bar_reward` | 0 | Constant downbeat reward |
| `downbeat_agreement_threshold` | 0.6 | Fall back to snapped direct downbeats below this agreement |
| `downbeat_agreement_tolerance` | 0.07 s | Event tolerance for that agreement check |

## Selection protocol

The staged search evaluated 918 complete candidates. It searched duration strength/tolerance, meter decoding, direct-path agreement, fallback bounds, and a final one-field refinement. Selection used an unweighted macro mean over pieces, with a 0.0005 absolute F1 guard and deterministic lexicographic tie breaking. All 64 calibration-subset selections (7 one-fold, 21 two-fold, 35 four-fold, and one seven-fold) were locked before the fixed SMC-fold-0 and GTZAN panels were opened.

The 7F default is preferred because it uses all available calibration folds and is the maximally supported global setting. It is not chosen because of a favorable GTZAN score. The aggregate eight-fold SMC result is out-of-fold with respect to backbone training, but it is **not** a nested estimate of decoder calibration because folds 1--7 informed the decoder configuration.

Older experiment bundles may contain the historical settings `duration_weight=12`, `uncertain_sigma=0.2`, and `fallback_minimal_ratio=0.9`, or an intermediate `duration_sigma=0.12`. Those are not release defaults.
