# CASM Introduction + Related Work — Option A: balanced, reviewer-facing

> Prepared by **terra** on 2026-09-13.  
> Intended use: the default recommendation. It gives the Introduction a general, functional opening while keeping the technical novelty and the PLPDP boundary precise.

## Copy-ready LaTeX

### Introduction — four paragraphs

```latex
\section{Introduction}
\label{sec:intro}

Beat tracking estimates when musical beats occur in an audio recording---the perceptual pulse to which a listener may naturally tap. That pulse helps people follow a performance and provides a temporal reference for tasks such as music transcription and structural analysis \cite{chiu2023localperiodicity,ru2026beatmamba}. A clear, steady beat can be easy to follow, yet automatic tracking remains difficult when expressive timing, weak or blurred onsets, dense polyphonic textures, or more than one plausible metrical interpretation obscure the pulse \cite{chiu2023localperiodicity,ru2026beatmamba,foscarin2026masked}. Such cases keep beat tracking an open problem, even as performance on standard benchmarks improves \cite{ahn2026smcblindspot}.

Most contemporary systems first turn audio into framewise beat activations and then decode them into an event sequence. In the common DBN formulation, inference follows a trajectory through a discretized tempo--phase--meter state space with globally specified tempo support, transition behaviour, and allowable meters \cite{krebs2015dbn,bock2016joint}. These constraints can promote coherence when they match a recording, but may conflict with activation-supported events under expressive timing or an unsupported tempo or meter \cite{foscarin2024beat,ahn2026smcblindspot}. PLPDP offers an important local alternative: it derives a time-varying estimated inter-beat interval and periodicity confidence from predominant local pulses (PLP), then replaces the fixed target and weight of dynamic programming with those local quantities \cite{chiu2023localperiodicity}. This establishes the value of conditioning a timing constraint on local evidence. However, pulse strength does not directly quantify whether the leading local period is decisively separated from its strongest competitor.

We introduce \emph{Context-Aware Semi-Markov} (CASM) decoding for this setting. CASM constructs a sparse path over activation-supported peaks and estimates, at each candidate, both a local period and the separation of its leading period hypothesis from its strongest competitor. This margin controls the strength and tolerance of a candidate-to-candidate duration cost: decisive periodic evidence supports firm local regularity, whereas competing hypotheses relax the constraint and let the activation evidence lead. A separate event-count safeguard returns the Direct path only when the structured result is implausibly sparse or dense. Figure~\ref{fig:casm-examples} visualises the intended behaviour: CASM can recover weak but activation-supported beats when periodicity is decisive, while under competing periodic evidence its output agrees with Direct.

CASM is a deterministic plug-in for compatible frozen activation streams: it requires neither backbone retraining nor per-track BPM or meter settings. One global decoder configuration is selected on development data and then frozen; at test time, its effective duration constraint still responds to each recording's local evidence. At a higher level, the fixed constants specify a reusable \emph{response rule}---how strongly to trust an input-derived period---rather than one corpus-specific tempo rigidity. This input-conditioned design is intended to make the configuration portable across recordings, backbones, and datasets; we evaluate that deployment contract and release the implementation together with a ready-to-use configuration.\footnote{Code and demo are available at \url{https://zhanh-he.github.io/casm-icassp2026-plot}.}
```

### Figure 1: in-text sentence and caption

Use the Fig.~1 sentence already embedded in paragraph three. Replace the current caption with:

```latex
\caption{Two held-out excerpts illustrating the input-conditioned behaviour of CASM on Beat This activations from SMC. A well-separated local period can support recovery of weak, activation-supported reference beats; when period hypotheses compete, the duration term relaxes and the CASM path coincides with Direct in this example. DBN and PLPDP traces are included for comparison. Reference annotations and reference IBI are shown only for interpretation and are not inputs to any decoder.}
```

This deliberately avoids repeating “left” and “right”: the panel layout already carries that information.

### Related Work — three paragraphs

```latex
\section{Related Work}
\label{sec:related}

Structured post-processors have long converted framewise beat evidence into event sequences. Dynamic programming balances onset evidence against a prescribed inter-beat regularity \cite{ellis2007beattracking}, while probabilistic beat-position models offer an alternative event-extraction formulation \cite{korzeniowski2014crf}; resonating comb filters estimate periodicity before alignment \cite{bock2015combfilter}. DBNs jointly model tempo, phase, and meter to decode globally consistent beat/downbeat paths \cite{krebs2015dbn,bock2016joint}. Semi-Markov state spaces have likewise been used for efficient causal joint rhythm inference \cite{heydari2022semimarkov}. These methods differ in state representation and inference, but each places an explicit temporal model outside the activation predictor.

The closest lineage to CASM is local-periodicity decoding. Predominant Local Pulse (PLP) estimates a time-varying pulse from locally periodic onset or activation evidence \cite{grosche2011plp}. PLPDP converts PLP peak spacings and heights into a local inter-beat-interval target and a pulse-strength confidence, respectively, and uses both in dense-frame dynamic programming \cite{chiu2023localperiodicity}. Thus, PLPDP already weakens its rhythm penalty when PLP evidence is weak; its confidence does not, however, explicitly quantify the separation between leading and competing period hypotheses. Subsequent PLP work made pulse estimation causal and controllable \cite{meier2024realtime}, while dPLP replaces hard period selection with a differentiable mixture of candidate kernels \cite{chiu2025dplp}. CASM therefore does not claim ambiguity handling in general as new. Instead, it uses a top-versus-runner-up period margin to regulate both the strength and tolerance of a sparse candidate-to-candidate duration cost, with a separate event-count safeguard that can return Direct.

Other work reduces dependence on a conventional decoder through different deployment choices. Particle-filter systems perform online rhythm-state inference \cite{hainsworth2004particle,heydari2021beatnet,heydari2024beatnetplus}, and target-specific adaptation uses additional annotations to retune a tracker \cite{pinto2021userdriven,maia2022adapting}. Post-processing-free networks shift more temporal modelling into predictor training \cite{chen2022postprocessingfree,foscarin2024beat}; masked diffusion explicitly models competing beat grids through learned iterative inference \cite{foscarin2026masked}. CASM instead targets the setting in which a frozen tracker has already supplied activations: it is a deterministic plug-in decoder, and it decodes downbeats on the selected beat grid without retraining the backbone.
```

## Why this option works

- Paragraph 1 begins with the human/function-level definition of beat tracking, not a disagreement with DBNs or a result metric.
- Paragraph 2 says exactly what PLPDP says about fixed global tempo assumptions, without claiming that a DBN is never adaptive or that PLPDP has no confidence mechanism.
- Paragraph 3 explains the mechanism once, and the figure sentence explains its two behaviours without narrating its layout.
- Paragraph 4 gives the reader a deployment-level reason for potential portability: CASM's global values govern an input-conditioned response rule. It intentionally does **not** claim that CASM is intrinsically less calibration-sensitive than DBNs; the present calibration comparison is not fully protocol-matched.
- The Related Work has a distinct job: historical positioning, the precise PLP--PLPDP--dPLP lineage, then competing deployment routes. It does not re-run the Introduction's problem statement.
