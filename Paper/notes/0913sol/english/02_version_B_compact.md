# CASM Introduction + Related Work — Version B

**Authoring model:** GPT-5.6 Sol  
**Positioning:** compact ICASSP version  
**Structure:** exactly four Introduction paragraphs and three Related Work paragraphs

This version is intended for a tight page budget. It preserves the novelty boundary around PLPDP and dPLP, but removes most secondary history and detailed deployment qualifiers from the paper text.

## Copy-ready LaTeX

```latex
\section{Introduction}
\label{sec:intro}

Beat tracking locates the perceptual pulses to which a listener might tap, and downbeat tracking identifies which pulses mark bar beginnings. The resulting timeline supports music transcription, structural analysis, synchronization, and interactive applications \cite{chiu2023localperiodicity,foscarin2024beat}. Modern systems commonly estimate framewise beat/downbeat activations and then decode them into discrete events \cite{bock2016joint}. The decoder must preserve credible activation evidence while producing a rhythm that remains coherent over time.

Direct peak picking stays close to the activations but can leave missing, duplicated, or metrically inconsistent events. DBNs improve coherence by inferring tempo, phase, and meter under a predefined state support and transition law \cite{krebs2015dbn,bock2016joint}. These settings are effective when they match the input music, yet can override correct local evidence under unusual meter, slow tempo, or expressive timing \cite{foscarin2024beat,ahn2026smcblindspot}. PLPDP instead derives a time-varying inter-beat interval and confidence from predominant local pulse and uses them to adapt the target and weight of a dynamic-programming penalty \cite{chiu2023localperiodicity}; the remaining issue is how much to trust that estimate when another metrical interpretation is almost as plausible.

CASM addresses this issue with a sparse semi-Markov path over activation-supported peaks. It estimates the leading local period and its separation from the strongest competitor, then uses that margin to control both the strength and tolerance of the segment-duration preference. Decoding in ambiguous regions consequently follows the activations more closely rather than being forced onto an uncertain grid. A separate beat-count safeguard returns the Direct path when the structured result is implausibly sparse or dense, while downbeats are decoded on the selected beat grid. Fig.~\ref{fig:casm-examples} illustrates these complementary operating regimes.

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{figures/p0.jpg}
\caption{Illustrative CASM decisions on out-of-fold Beat This activations on SMC. A clearly separated period allows CASM to recover weak but activation-supported events; competing periods weaken the duration preference and leave the activation-led path unchanged. Neither example triggers the independent count-ratio safeguard, and reference-derived tempo is displayed only for interpretation.}
\label{fig:casm-examples}
\end{figure}

CASM is calibrated once, but its fixed parameters define how each input controls the decoder rather than imposing one tempo target or transition rigidity on every track. In the reported experiments, we apply one frozen configuration across tracks and backbones without retraining or per-track BPM/meter tuning. We provide an interactive demo and will release the decoder implementation and configuration upon publication.

\section{Related Work}
\label{sec:related}

Dynamic programming established the standard balance between onset evidence and inter-beat regularity \cite{ellis2007beattracking}. Probabilistic beat extraction and resonating comb filters introduced alternative event- and periodicity-based formulations \cite{korzeniowski2014crf,bock2015combfilter}, while DBNs became the dominant joint beat/downbeat decoder by modelling tempo, phase, and meter in a state-space trajectory \cite{krebs2015dbn,bock2016joint}. Semi-Markov rhythm tracking has also been explored in a causal one-dimensional state space \cite{heydari2022semimarkov}. Together, these methods establish structured sequence inference as a long-standing complement to framewise activations.

PLP provides a time-varying pulse representation derived from locally dominant periodicity \cite{grosche2011plp}. Its use in PLPDP is CASM's closest methodological precedent: PLPDP uses the interval between adjacent PLP peaks as a piecewise local inter-beat interval and their mean height as confidence; the former supplies a time-varying target and the latter modulates the weight of a dense-frame dynamic-programming penalty \cite{chiu2023localperiodicity}. Thus PLPDP already weakens structure under low confidence, but does not explicitly compare the selected period with its strongest competitor. Later work adapted PLP to causal, zero-latency tracking \cite{meier2024realtime} and made period selection differentiable through dPLP's softmax-weighted combination of candidate kernels \cite{chiu2025dplp}. CASM's narrower contribution is an explicit period-separation margin that controls the strength and width of a sparse event-level duration cost, plus an independent beat-count safeguard and a beat-synchronous downbeat decoder.

Other routes change the deployment setting, the predictor, or the available supervision. Online particle-filter systems maintain tempo hypotheses during causal inference, while user-adaptive trackers learn from annotations \cite{heydari2021beatnet,heydari2024beatnetplus,pinto2021userdriven}. Post-processing-free networks and Beat This! are trained for minimal peak picking \cite{chen2022postprocessingfree,foscarin2024beat}, whereas masked diffusion models multiple plausible grids through iterative neural inference \cite{foscarin2026masked}. CASM instead retains a deterministic post-processing role for already trained models, requiring only their activation outputs and no additional backbone training.
```

## When to choose this version

- Choose it if the current paper is close to the ICASSP page limit.
- It keeps the strongest reviewer-facing citations while dropping BeatFCOS, target reformulation, the larger CRF history, and detailed calibration language.
- It still keeps dPLP; that citation is more important to the novelty argument than any of the omitted adjacent methods.
