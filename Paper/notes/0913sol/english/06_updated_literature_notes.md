# CASM literature notes for Introduction and Related Work

**Prepared by:** GPT-5.6 Sol  
**Date:** 2026-09-13  
**Scope:** local `reading/` corpus, 0913 notes, `casm_v4.tex`, and supporting audit notes

## Main conclusion

CASM is best positioned neither as “the first local-period decoder” nor as “the first ambiguity-aware beat tracker.” Its defensible contribution is the following combination:

> an explicit best-versus-competitor period margin, connected to the strength and tolerance of a sparse event-level duration model, with independent Direct and downbeat safeguards, for deterministic decoding of frozen backbone activations.

This sentence preserves the important PLPDP lineage, acknowledges dPLP and multiple-grid work, and still leaves CASM a clear technical and deployment identity.

## What the eight local papers teach about opening an Introduction

| Local reading | Opening pattern | Use for CASM |
| --- | --- | --- |
| `01_Beat_This_中文翻译.md`, lines 18--30 | Defines beat tracking, then downbeat tracking, then the common activation-plus-decoder pipeline | Primary structural model for P1 and the start of P2 |
| `02_BeatFM_中文翻译.md`, lines 24--30 | Defines the temporal-location task and names downstream uses before technical detail | Supports the transcription/structure/synchronization motivation |
| `03_HingeNet_中文翻译.md`, lines 30--44 | Describes beat as a temporal framework for music analysis | Supports “temporal scaffold” language |
| `04_SMC_Blind_Spot_中文翻译.md`, lines 18--26 | Gives a short definition, then the modern pipeline and failure gap | Useful for P2, but its benchmark number does not belong in P1 |
| `05_Masked_Diffusion_中文翻译.md`, lines 28--48 | Moves quickly to framewise prediction, multiple valid grids, and incoherent mixtures | Best used in Related Work, not as CASM's opening |
| `06_PLPDP_中文翻译.md`, lines 19--31 | Starts from perceived pulse, musical function, and the novelty/activation-plus-PPT pipeline | Primary source for a perceptual and functional opening |
| `07_BeatMamba_中文翻译.md`, lines 19--23 | Defines the task and frames local transient evidence versus long-range rhythmic coherence | Useful conceptual bridge into the decoding problem |
| `08_Chopin_Mazurkas_中文翻译.md`, lines 18--24 | Contrasts effortless human tapping with fragile automatic tracking across expressive styles | Most human-readable alternative opening |

The corpus-level consensus is: **define the perceptual task, say what the output enables, then introduce the technical pipeline or difficulty.** Specific F1 values, named decoder failures, model complexity, and contribution claims come later.

## DBN: what is fixed and what adapts

The literature does not support saying that a DBN uses one fixed tempo trajectory. Its decoded state path adapts to observations and can move through tempo, bar-position/phase, and meter states. What is configured globally is:

- admissible tempo support;
- admissible meter support in joint beat/downbeat formulations;
- the form and stiffness of the tempo-transition law;
- observation/transition weighting and other decoder settings.

PLPDP's criticism is specifically that common HMM/DBN transition likelihoods are empirically chosen at a global level and may be too rigid for expressive local tempo changes. Beat This! broadens the critique to unsupported meters, out-of-range tempi, and genre-dependent tempo variability. SMC Blind Spot adds an essential qualification: a DBN support mismatch can force octave-level errors, but confidently wrong activations remain a major failure source. Therefore:

### Supported wording

> DBNs infer an observation-dependent metrical path under globally configured state support and transition preferences; when those assumptions mismatch the music, they can suppress correct local evidence.

### Unsupported wording

- “DBNs do not adapt to the input.”
- “DBNs assume the tempo is constant.”
- “DBNs are the main cause of SMC failure.”

## PLP lineage and CASM's exact boundary

| Method | Representation or uncertainty signal | Behaviour under ambiguity | Relationship to CASM |
| --- | --- | --- | --- |
| PLP \cite{grosche2011plp} | Locally dominant periodic kernel in a tempogram, overlap-added into a pulse curve | Hard local period selection can collapse competing explanations to one winner | Establishes the local-pulse representation; it is not itself a complete sequence decoder |
| PLPDP \cite{chiu2023localperiodicity} | PLP peak spacing gives piecewise local IBI; the mean height of neighbouring PLP peaks gives confidence | Lower confidence reduces the DP transition weight | Closest decoder predecessor; already has local target and confidence-weighted regularization |
| Real-Time PLP \cite{meier2024realtime} | Causal PLP with stability/lookahead/context outputs | Focuses on online controllability and zero latency | A subsequent PLP branch, not a direct revision of the PLPDP recurrence |
| dPLP \cite{chiu2025dplp} | Softmax weighting over period kernels | Competing kernels can interfere and weaken pulse peaks | Prevents a broad “first ambiguity-aware method” claim |
| CASM | Normalized score gap between the best local period and strongest non-neighbour competitor | Low margin weakens and widens the duration preference; a separate count test may return Direct | Makes competition explicit in a sparse event-level decoder and separates soft restraint from hard fallback |
| Masked diffusion \cite{foscarin2026masked} | Learned distribution over multiple plausible output grids | Iterative inference settles on a coherent grid | Handles ambiguity upstream through specialized neural training rather than a frozen-output plug-in |

### The most important PLPDP detail

In PLPDP, confidence is not just a vague “PLP confidence.” The PLP curve is segmented around detected peaks; local IBI comes from peak spacing, and the confidence of a segment is defined from the heights of its two boundary peaks (`06_PLPDP_全文中文翻译.md`, around lines 86--98). This confidence modulates the DP transition penalty. Therefore CASM cannot claim that PLPDP always enforces its selected period equally strongly.

The useful gap is narrower: high absolute PLP pulse strength does not explicitly mean that the chosen period is well separated from the strongest octave-related or neighbouring alternative. CASM's runner-up margin addresses that relational question.

## Soft restraint and hard fallback are different mechanisms

The present CASM algorithm has two levels of behaviour:

1. **Local soft restraint:** a small period margin reduces the duration coefficient and enlarges timing tolerance. The structured path becomes increasingly driven by candidate activation evidence.
2. **Global hard fallback:** only an anomalous structured-to-Direct event-count ratio returns the exact Direct path.

The right-hand Fig. 1 example matches Direct because the duration term becomes weak, not because ambiguity directly triggers a router. Neither displayed example fires the count safeguard. Wording such as “switches to Direct whenever ambiguity is high” would imply a nonexistent threshold and should be avoided.

## Structured-decoding history to retain

The first Related Work paragraph should keep only history that protects the paper's positioning:

- Ellis DP: canonical evidence-plus-inter-beat-prior formulation (`ellis2007beattracking`).
- CRF/probabilistic extraction: alternative structured sequence models (`korzeniowski2014crf`, optionally `fillon2015crf`).
- Resonating comb filters: explicit dominant-period estimation (`bock2015combfilter`), not a joint beat/downbeat decoder.
- DBN: standard neural activation + tempo/phase/meter state-space pipeline (`krebs2015dbn`, `bock2016joint`).
- Particle filters / BeatNet: causal online hypotheses (`hainsworth2004particle`, `heydari2021beatnet`, `heydari2024beatnetplus`).
- Heydari et al. 1D semi-Markov state space: proof that semi-Markov rhythm tracking predates CASM (`heydari2022semimarkov`).
- Reliability-informed tracking: evidence-quality-dependent commitment predates CASM's particular margin (`degara2012reliability`).

The historical paragraph should end with a design axis, not another citation: **where does the temporal prior come from, and is its effective constraint law globally fixed or conditioned on current evidence?**

## Alternatives outside the frozen-output setting

The third Related Work paragraph should separate CASM from methods that change a different part of the system:

- Post-processing-free networks and Beat This! move more temporal responsibility into predictor training (`chen2022postprocessingfree`, `foscarin2024beat`).
- Masked diffusion learns to represent and resolve several valid grids (`foscarin2026masked`).
- BeatFCOS and target-reformulation work redesign the output representation (`ahn2025beatfcos`, `bolt2026reformulated`).
- User/corpus adaptation adds annotations or domain-specific tuning (`pinto2021userdriven`, `maia2022adapting`, `maia2024selective`, `pinto2026challenging`).

These are not inferior versions of the same solution. They answer different deployment questions. CASM's setting is specifically: an already trained compatible tracker is frozen, its activation outputs are available, and one wants transparent deterministic sequence decoding without retraining.

## Claim ladder for the paper

### Strong and supportable

- CASM uses an explicit top-versus-competitor local-period margin.
- This margin modulates both strength and tolerance of the duration cost.
- The decoder searches activation-supported candidate events.
- Local ambiguity softens the structured term; count fallback is independent.
- The same globally calibrated configuration is frozen across the reported tracks, datasets, and backbones.
- No per-track labelled BPM/meter input or decoder update is used at inference.

### Supportable only with careful qualification

- Lower calibration burden: attribute it to the observed frozen-policy deployment and, if protocol-matched, selection sensitivity.
- Better generalization: say transfer across the evaluated corpora/backbones, not universal domain generalization.
- Open and ready to use: say this only once implementation, license, frozen config, input contract, and minimal example are public.

### Avoid

- First local-period beat decoder.
- First ambiguity-aware beat tracker.
- Parameter-free or tuning-free.
- Ambiguity directly switches CASM to Direct.
- Semi-Markov structure inherently generalizes better than DBN.
- Real-Time PLP or dPLP is a direct PLPDP sequel.

## Recommended section-level separation

- **Introduction:** functional definition; Direct/DBN tension; one-sentence PLPDP bridge; CASM mechanism; concise deployment ending.
- **Related Work:** structured-decoder history; detailed PLP/PLPDP/dPLP lineage; predictor/adaptation alternatives.
- **Methodology:** formal margin, endpoint aggregation, duration cost, DP, and exact safeguard rules.
- **Experiments/Results:** scores, matched support, calibration protocol, sensitivity, and transfer evidence.

This allocation keeps PLPDP prominent without repeating the same local-IBI/confidence explanation in both Introduction and Related Work.

