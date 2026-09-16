# CASM Introduction + Related Work — Version C

**Authoring model:** GPT-5.6 Sol  
**Positioning:** stronger policy/generalization narrative  
**Structure:** exactly four Introduction paragraphs and three Related Work paragraphs

This version makes one conceptual question carry the Introduction: **when has rhythmic regularity earned the right to override local evidence?** It gives CASM a more memorable identity while retaining conservative technical claims.

## Copy-ready LaTeX

```latex
\section{Introduction}
\label{sec:intro}

The musical beat is a perceptual pulse that listeners can follow or tap along with, providing a temporal framework for organizing rhythm. Beat tracking estimates the times of these pulses from audio, while downbeat tracking identifies the pulses that begin bars. Together, their outputs form a temporal reference for transcription, structural analysis, synchronization, editing, and interactive music applications \cite{chiu2023localperiodicity,foscarin2024beat}. Although listeners often follow a beat effortlessly, an automatic system must remain reliable across weak cues, expressive timing, and competing metrical interpretations.

Most current trackers separate this task into evidence estimation and sequence decoding: a neural network produces framewise activations, and a decoder turns them into event times \cite{bock2016joint}. Direct peak picking closely follows local activations but does not itself enforce long-range rhythmic coherence. DBN decoding improves coherence but introduces a complementary risk: it stabilizes a tempo--phase--meter path under globally specified state support and transition preferences \cite{krebs2015dbn,bock2016joint}. The path still responds to the observations, yet the form and strength of those preferences are not themselves conditioned on the reliability of local periodic evidence; mismatched settings can therefore suppress useful activations \cite{foscarin2024beat,ahn2026smcblindspot}. PLPDP instead derives a time-varying inter-beat interval and confidence from predominant local pulse and uses them to adapt the target and weight of a dynamic-programming penalty \cite{chiu2023localperiodicity}. The unresolved decision is not only which local period is strongest, but whether it is sufficiently better than the alternatives to justify enforcing it.

CASM treats rhythmic regularity as a commitment that must be earned by the input. It builds a sparse semi-Markov path over activation-supported peaks, estimates a local period around each peak, and measures how clearly that period outranks its strongest competitor. A decisive margin yields a narrow, strong duration preference; a small margin yields a broad, weak one, so the path becomes increasingly observation-led rather than committing to an arbitrary metrical level. The count safeguard and beat-synchronous downbeat decoder address separate path-level failures. Fig.~\ref{fig:casm-examples} contrasts these two evidence-dependent decoding regimes.

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{figures/p0.jpg}
\caption{Illustrative CASM decisions on out-of-fold Beat This activations on SMC. Weak but activation-supported events are recovered when one period is clearly separated; when period hypotheses compete, the duration constraint weakens and the activation-led path is preserved. Neither example triggers the independent count-ratio safeguard. Reference-derived tempo is shown only for interpretation and is not used by CASM.}
\label{fig:casm-examples}
\end{figure}

CASM is therefore a decoder policy rather than a corpus-specific rhythm template: global scalars fix an evidence-to-constraint response law, and each activation sequence determines its effective period target and rigidity. After one global calibration, we apply the same configuration across tracks, corpora, and frozen backbones without retraining or per-track BPM/meter settings; Sec.~\ref{sec:exp} separately evaluates its sensitivity to the composition of the calibration data. We provide an interactive demo and will release the decoder implementation and frozen configuration upon publication.

\section{Related Work}
\label{sec:related}

\subsection{Where rhythmic structure enters the decoder}
Early dynamic-programming trackers combined onset evidence with a dominant inter-beat prior \cite{ellis2007beattracking}. Probabilistic beat extraction, CRFs, and comb-filter methods introduced alternative event or periodicity representations \cite{korzeniowski2014crf,fillon2015crf,bock2015combfilter}. DBNs subsequently established the prevalent neural-activation-plus-state-space pipeline, jointly resolving tempo, phase, and meter \cite{krebs2015dbn,bock2016joint}. Particle filters maintain causal tempo hypotheses \cite{hainsworth2004particle}; BeatNet/BeatNet+ and a one-dimensional semi-Markov state space extend causal inference to joint rhythm analysis \cite{heydari2021beatnet,heydari2022semimarkov,heydari2024beatnetplus}. CASM inherits the common goal of reconciling local evidence with sequence structure; its use of semi-Markov segments is therefore not, by itself, the novelty claim.

\subsection{From local pulse to evidence-dependent commitment}
Predominant local pulse (PLP) extracts a time-varying pulse by selecting locally salient periodic kernels \cite{grosche2011plp}. PLPDP uses the interval between adjacent PLP peaks as a piecewise local inter-beat interval and the mean height of those peaks as confidence; the former supplies a time-varying target and the latter modulates the weight of a dense-frame dynamic-programming penalty \cite{chiu2023localperiodicity}. It is thus the closest methodological predecessor to CASM and already establishes confidence-weighted local decoding. The distinction is what the confidence represents: PLPDP measures support in the selected pulse curve, whereas CASM explicitly measures the selected period against the next-best period hypothesis. Later work adapted PLP to causal, zero-latency tracking \cite{meier2024realtime}; dPLP made period selection differentiable through a softmax-weighted combination of candidate kernels \cite{chiu2025dplp}. CASM does not claim the broad idea of period ambiguity as new. It connects a transparent competitor margin to both the strength and tolerance of a sparse event-to-event duration potential, then handles anomalous event counts and downbeats with separate deterministic safeguards.

\subsection{Changing the predictor or supervision}
Several alternatives place rhythmic structure in the predictor or obtain it from additional information. User-driven methods adapt trackers from annotations \cite{pinto2021userdriven,maia2022adapting,maia2024selective,pinto2026challenging}. Post-processing-free networks, including Beat This!, train the predictor for minimal peak picking \cite{chen2022postprocessingfree,foscarin2024beat}; masked diffusion instead learns a distribution over plausible grids and resolves one through iterative inference \cite{foscarin2026masked}; interval-object and target-reformulation methods further redesign the prediction problem \cite{ahn2025beatfcos,bolt2026reformulated}. These approaches are complementary, but generally change the predictor, its training, or the supervision available at adaptation time. CASM isolates the decoder: it operates deterministically on the outputs of a frozen tracker and can therefore be attached without retraining the upstream model.
```

## When to choose this version

- Choose it if you want the paper to be remembered for a single idea: **regularity should be evidence-conditioned, not uniformly imposed**.
- The final paragraph gives the clearest high-level explanation of lower calibration burden: global parameters determine a response policy; local evidence determines the actual operating point.
- The phrase “evaluated in this work” deliberately treats calibration sensitivity as empirical support, not as a theorem about all semi-Markov models.
