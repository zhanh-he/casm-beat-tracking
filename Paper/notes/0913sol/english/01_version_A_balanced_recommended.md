# CASM Introduction + Related Work — Version A

**Authoring model:** GPT-5.6 Sol  
**Positioning:** balanced and recommended  
**Structure:** exactly four Introduction paragraphs and three Related Work paragraphs  
**Source base:** `casm_v4.tex`, the three 0913 notes, the local `reading/` collection, and the calibration/mechanism audits

This version keeps the strongest parts of `casm_v4` but gives the Introduction a functional, reader-friendly opening. It reserves the detailed PLP lineage for Related Work and makes the final Introduction paragraph a compact deployment statement.

## Copy-ready LaTeX

```latex
\section{Introduction}
\label{sec:intro}

Beat tracking estimates the time positions of the perceptual pulses to which listeners naturally tap, while downbeat tracking additionally identifies the beginning of each bar \cite{chiu2023localperiodicity,foscarin2024beat}. Together, these events provide a temporal scaffold for following and organizing musical rhythm and support applications such as music transcription, structure analysis, synchronization, and interactive music systems. Although listeners often perceive a beat effortlessly, reliable automatic tracking remains difficult when acoustic cues are weak, timing changes expressively, or several metrical interpretations are plausible.

Most contemporary trackers first map audio to framewise beat and downbeat activations before decoding these curves into discrete events \cite{bock2016joint}. A minimal decoder selects local activation maxima, preserving the network's local decisions but offering little protection against duplicated, missed, or metrically inconsistent events \cite{foscarin2024beat}. Dynamic Bayesian networks (DBNs) instead infer a joint tempo--phase--meter trajectory and remain the standard way to impose temporal coherence \cite{krebs2015dbn,bock2016joint}. Their inferred trajectory depends on the observations, but its tempo support, admissible meters, and transition law are specified globally before a track is seen; when these assumptions mismatch very slow, expressively timed, or structurally unusual music, the prior can suppress otherwise useful local evidence \cite{foscarin2024beat,ahn2026smcblindspot}. PLPDP showed that a decoder's timing constraint can instead be derived from local periodic evidence \cite{chiu2023localperiodicity}. This raises a further question: how much rhythmic commitment has that evidence earned when several metrical interpretations remain plausible?

We introduce CASM, a context-aware semi-Markov decoder that searches a sparse graph of activation-supported candidate events. Around each candidate, it compares the dominant local period with the strongest alternative and uses this competition to grade event-to-event rhythmic commitment. As the separation narrows, the duration preference weakens and the decoded path increasingly follows the activations. A separate beat-count safeguard returns the Direct path when the structured result is implausibly sparse or dense, while a beat-synchronous meter decoder preserves beat--downbeat consistency. Fig.~\ref{fig:casm-examples} makes these behaviours concrete on held-out activations.

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{figures/p0.jpg}
\caption{Illustrative CASM decisions on out-of-fold Beat This activations on SMC. A clearly separated period allows CASM to recover weak but activation-supported events, whereas competing periods weaken the duration preference and leave the activation-led path unchanged. Neither example triggers the independent count-ratio safeguard; reference-derived tempo is shown only for interpretation and is not used by the decoder.}
\label{fig:casm-examples}
\end{figure}

CASM replaces per-track timing assumptions with a decoder policy fixed after a single global calibration: its global constants specify how local evidence should control the decoder rather than prescribing one effective rhythmic regime for every input. Because each activation sequence determines its local target and constraint strength, we evaluate the same configuration across recordings, corpora, and backbone models without per-track calibration at inference. We provide an interactive demo and will release the decoder implementation and frozen configuration upon publication.

\section{Related Work}
\label{sec:related}

\subsection{Structured post-processing}
Beat-tracking post-processors have long treated event extraction as sequence inference. Dynamic programming balances onset evidence against an inter-beat regularity prior \cite{ellis2007beattracking}; Bayesian and CRF-based extractors infer beat positions from activation functions \cite{korzeniowski2014crf,fillon2015crf}; and resonating comb-filter banks provide explicit dominant-period estimates \cite{bock2015combfilter}. DBNs became the standard joint decoder by representing tempo, phase, and meter in a temporally coherent state trajectory \cite{krebs2015dbn,bock2016joint}. Particle filters maintain causal tempo hypotheses \cite{hainsworth2004particle}; BeatNet/BeatNet+ and a compact semi-Markov state space extend causal inference to joint rhythm analysis \cite{heydari2021beatnet,heydari2022semimarkov,heydari2024beatnetplus}. Although these approaches differ in representation and inference, they share the premise that noisy framewise evidence should be interpreted as a sequence rather than thresholded independently.

\subsection{Local periodicity and competing interpretations}
Reliability-informed tracking established the broader idea that temporal commitment can depend on evidence quality \cite{degara2012reliability}. The closest methodological lineage to CASM then begins with predominant local pulse (PLP), which constructs a time-varying pulse representation from locally dominant periodicities \cite{grosche2011plp}. PLPDP uses the interval between adjacent PLP peaks as a piecewise local inter-beat interval and the mean height of those peaks as confidence; the former supplies a time-varying target and the latter modulates the weight of a dense-frame dynamic-programming penalty \cite{chiu2023localperiodicity}. PLPDP therefore already relaxes temporal structure when its confidence is low. Its confidence, however, reflects pulse salience rather than the separation between the selected period and the strongest competing interpretation. Subsequent work adapted PLP to causal, zero-latency tracking \cite{meier2024realtime}, while dPLP replaced hard period selection with a softmax-weighted combination of periodic kernels, allowing competing hypotheses to jointly shape the pulse representation \cite{chiu2025dplp}. CASM consequently does not claim ambiguity handling in general as new. Its distinction is to use an explicit top-versus-competitor period margin to control both the strength and tolerance of a sparse event-to-event duration cost, while an independent event-count safeguard can return the Direct path and a beat-synchronous decoder handles downbeats.

\subsection{Changing the predictor or supervision}
Other work reduces reliance on a conventional fixed decoder by changing what the predictor learns or by adding adaptation data. User-driven systems tune a tracker from annotations \cite{pinto2021userdriven,maia2022adapting,maia2024selective,pinto2026challenging}. Post-processing-free networks, including Beat This!, move more temporal modelling into the predictor \cite{chen2022postprocessingfree,foscarin2024beat}; masked diffusion learns to resolve competing output grids through iterative inference \cite{foscarin2026masked}; and interval-object or reformulated targets change what the network predicts \cite{ahn2025beatfcos,bolt2026reformulated}. These approaches therefore occupy a different deployment setting from CASM, which changes only the decoding applied to an already-frozen activation stream.
```

## Why this is the recommended version

- The opening follows the dominant pattern in the reading set: define the task, explain its function, then introduce the modern pipeline.
- The DBN sentence explicitly acknowledges that its latent trajectory is observation-dependent; only the support and transition law are globally specified.
- Introduction mentions PLPDP only at the level needed to expose the unresolved question. Related Work owns its IBI/confidence mechanism and the full PLP lineage.
- The figure is introduced once at the level of purpose. Its caption carries the concrete cases and states that neither example is a count-safeguard fallback.
- The closing paragraph explains transfer at the policy level without calling CASM parameter-free or claiming that semi-Markov structure intrinsically guarantees generalization.
