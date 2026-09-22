# CASM Introduction Paragraphs 3-4: English A/B/C Versions

## Recommendation

**Version A is recommended and has been inserted into `casm_v4.tex`.** It gives the most precise account of the methodological progression while keeping the Introduction readable:

> globally configured temporal constraints -> PLPDP's locally adaptive target and weight -> CASM's relative ambiguity margin and sparse segmental search.

The key distinction is not that CASM introduces local confidence or weakens an unreliable temporal prior; PLPDP already does both. The defensible distinction is the **semantics of the conditioning signal**:

- PLPDP derives its local IBI from the spacing of adjacent peaks in a PLP curve and its confidence from their mean height. Its dynamic-programming condition receives the selected IBI and this non-comparative strength measure.
- CASM evaluates the local autocorrelation response over all admissible lags at each retained activation maximum. It selects the best lag and computes a normalized margin between that score and the strongest alternative outside a small lag neighborhood. This is a relative separation measure.
- CASM does not maintain several tempo paths. It uses the alternative only to decide how stiff the duration cost around the selected period should be. Low margin weakens the temporal cost; it does not by itself invoke the Direct fallback.

## Technical comparison behind the wording

| Dimension | PLPDP | CASM |
|---|---|---|
| Local period | The default implementation synthesizes PLP curves from the predominant Fourier-tempogram component at 1, 3, and 5 s scales, multiplies them, and takes adjacent PLP-peak spacing as the local IBI. | Normalized local autocorrelation is evaluated over the admissible lag range at each activation-peak candidate; the best lag is the local period. |
| Conditioning signal | $\lambda(n)$ is the mean height of two adjacent PLP peaks. It measures the strength/consistency of the selected pulse curve but contains no explicit runner-up comparison. | $c_i$ is the clipped normalized margin between the best lag score and the strongest score outside $\pm2$ lag frames. It measures separation from a competing local explanation. |
| Use in the temporal term | $\hat{\delta}(n)$ centers the log-IBI penalty and $\lambda(n)$ multiplies it at the current DP frame. | Endpoint periods and margins are combined geometrically for an edge. The margin acts through both a multiplicative factor and an ambiguity-dependent scale in the log-duration cost. |
| Search space | Dense-frame dynamic programming can place a beat at any frame. | Sparse semi-Markov dynamic programming selects a path only through retained activation maxima; edges represent complete inter-beat segments. |
| What ambiguity means | Ambiguity may affect the PLP peak height indirectly, but competing period scores are not explicitly compared in the DP condition. | Competition is explicitly summarized by a top-versus-alternative margin, but CASM remains a single-period, single-path decoder rather than full multi-hypothesis tempo inference. |
| Fallback | The PLPDP recurrence may restart from the current frame. | CASM may restart during DP and separately returns the Direct path only when the final CASM/Direct beat-count ratio falls outside fixed bounds. |

Implementation anchors: [CASM local lag scoring and margin](https://github.com/zhanh-he/casm-beat-tracking/blob/paper-revisions/src/casm_beat_tracking/decoder.py#L98-L179), [CASM sparse edge cost](https://github.com/zhanh-he/casm-beat-tracking/blob/paper-revisions/src/casm_beat_tracking/decoder.py#L294-L344), [PLPDP IBI/confidence construction](https://github.com/SunnyCYC/plpdp4beat/blob/main/modules.py#L80-L140), and [PLPDP recurrence](https://github.com/SunnyCYC/plpdp4beat/blob/main/modules.py#L180-L253).

Source-level caveat: the PLPDP paper defines $\lambda(n)$ as time varying. Its reference code caches the weighted penalty and refreshes the confidence factor only when the integer local IBI changes ([lines 224-230](https://github.com/SunnyCYC/plpdp4beat/blob/main/modules.py#L224-L230)); a confidence-only segment change with the same integer IBI therefore does not refresh that cache. The Introduction follows the published algorithmic definition, because this implementation detail is not the conceptual distinction on which the CASM claim should depend.

## Version A - technically explicit (recommended)

### Paragraph 3

> PLPDP~\cite{chiu2023localperiodicity} represents an important step toward locally adaptive post-processing. It converts predominant local pulse (PLP) into a time-varying IBI $\hat{\delta}(n)$ and confidence $\lambda(n)$: the former centers the tempo-consistency penalty, while the latter scales it according to the mean heights of adjacent PLP peaks. PLPDP therefore already adapts both the target and strength of the temporal constraint. Its confidence, however, is a non-comparative measure: the dynamic-programming condition contains no explicit term for how decisively the selected periodicity exceeds a competing interpretation. The relative uncertainty between, for example, half- and double-tempo hypotheses can thus remain implicit when they receive similar local support.

### Paragraph 4

> We introduce CASM, a context-aware semi-Markov post-processor that makes this comparison explicit. At each retained activation maximum, CASM scores the admissible autocorrelation lags, selects the strongest as the local period, and computes a normalized margin to the strongest alternative outside a small lag neighborhood. This margin is not a calibrated probability and does not create a multi-hypothesis tempo path; instead, through a multiplicative weight and an ambiguity-dependent scale, it controls the stiffness of the duration cost centered on the selected period. CASM combines the period and margin at both endpoints of each candidate-to-candidate segment. A clear winner yields a strong duration preference that can recover weak but activation-supported beats, whereas a small margin flattens that preference so activation evidence dominates while periodicity remains unresolved. Fig.~\ref{fig:casm-examples} illustrates these two regimes. A deterministic beat-count safeguard and beat-synchronous meter stage further stabilizes the output. CASM is model-agnostic, requires no neural-network retraining, and is provided as a pip-installable reference implementation with a madmom-style activation interface.

Why choose A: it states the actual PLPDP quantities, identifies the non-comparative versus relative distinction, and explicitly limits the CASM claim to a single-path ambiguity gate.

## Version B - reader-first

### Paragraph 3

> PLPDP~\cite{chiu2023localperiodicity} provides an important bridge from fixed to locally adaptive post-processing. It extracts both a local IBI and a confidence from predominant local pulse (PLP), using the former to set the preferred interval and the latter to scale the temporal penalty. PLPDP therefore already knows when its selected pulse is strong. What it does not explicitly ask is how decisively that pulse is preferred over another plausible period. This distinction matters when, for example, half- and double-tempo interpretations both fit the local activation pattern: the selected pulse may be salient even though the metrical interpretation is not unique.

### Paragraph 4

> CASM addresses this distinction with an ambiguity-conditioned semi-Markov post-processor. Around every retained activation peak, it compares the best local autocorrelation lag with the strongest alternative outside a small lag neighborhood and converts their relative margin into the stiffness of an event-to-event duration preference. CASM therefore follows a clear local period strongly enough to recover weak activation-supported beats, but relies more heavily on activation evidence when no period wins decisively. The search remains a single sparse path over observed maxima rather than a multi-hypothesis tempo model, and Direct is used only by a separate beat-count safeguard. Fig.~\ref{fig:casm-examples} shows the two operating regimes. The resulting post-processor is deterministic and model-agnostic, requires no neural-network retraining, and is provided through a pip-installable reference implementation with a madmom-style interface.

Why choose B: it leads with the conceptual question and postpones the implementation details, making it easier to read outside the beat-tracking community.

## Version C - compact camera-ready

### Paragraph 3

> PLPDP~\cite{chiu2023localperiodicity} makes post-processing locally adaptive by deriving a time-varying IBI and confidence from predominant local pulse (PLP). The IBI sets the target of its dynamic-programming penalty, while confidence---the mean height of adjacent PLP peaks---sets its weight. This confidence measures the selected pulse without explicitly comparing it with a competing periodic interpretation, so relative ambiguity such as half-/double-tempo competition remains implicit.

### Paragraph 4

> We introduce CASM, a sparse semi-Markov post-processor that conditions temporal regularity on this missing comparison. At each activation-peak candidate, CASM takes the best local autocorrelation lag as the period and uses its normalized margin over the strongest alternative outside a small lag neighborhood to control the stiffness of candidate-to-candidate duration costs. Clear separation strengthens local regularity; weak separation lets activation evidence dominate, without claiming multi-hypothesis tempo inference or automatically reverting to Direct. Fig.~\ref{fig:casm-examples} illustrates both regimes. CASM is deterministic, model-agnostic, requires no retraining, and is provided as a pip-installable reference implementation with a madmom-style activation interface.

Why choose C: it preserves the exact novelty boundary with the smallest page-budget cost.

## Claims deliberately removed or narrowed

- Removed the claim that PLPDP adapts only local tempo: it also adapts the penalty weight.
- Replaced generic "confidence" language with the exact distinction between PLP peak height and best-versus-alternative separation.
- Avoided saying that CASM maintains multiple tempo hypotheses or solves metric-level switching.
- Treated half-/double-tempo competition as an example, not as the only alternative considered or as a solved failure mode.
- Avoided saying that ambiguity automatically makes CASM return the Direct path; that happens only through the separate count-ratio safeguard.
- Replaced "target, strength, and tolerance" as three independent controls with the exact statement that one margin changes duration-cost stiffness through a multiplicative factor and an ambiguity-dependent scale.
- Removed the unsupported MIREX-generalization claim and the causal claim that CASM intrinsically requires less tuning than DBN.
- Replaced "compatible with madmom" with the narrower, implementation-accurate phrase "madmom-style activation interface."
- Replaced "released as open source" with "provided as a reference implementation" because the public repository still lists license selection and the first PyPI release as pending.
