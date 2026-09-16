# CASM Introduction + Related Work — Option C: compact, evidence-safe

> Prepared by **terra** on 2026-09-13.  
> Intended use: choose this if space is tight or if you want the most conservative formulation of portability and calibration. It is the least vulnerable to a reviewer asking what the current calibration experiment actually establishes.

## Copy-ready LaTeX

### Introduction — four paragraphs

```latex
\section{Introduction}
\label{sec:intro}

Music often invites us to tap, move, or anticipate the next event before it arrives. Automatic beat tracking seeks to recover the pulse behind this experience from audio, giving music technologies a time reference for transcription, structural analysis, and responsive applications. The task is straightforward only when the pulse is explicit and regular. In expressive or unusual passages, tempo changes, weak attacks, dense textures, or competing ways of hearing the pulse can leave no single obvious answer; a neural model may then produce predictions that make sense one moment at a time but not as one stable rhythmic interpretation \cite{chiu2023localperiodicity,ru2026beatmamba,foscarin2026masked}.

A common solution is a dynamic Bayesian network (DBN), which decodes a joint tempo, phase, and meter trajectory under globally specified state support and transition assumptions \cite{krebs2015dbn,bock2016joint}. Such structure can correct local errors when those assumptions fit the recording, but it can also reject activation-supported events when tempo, meter, or timing behaviour falls outside them \cite{foscarin2024beat,ahn2026smcblindspot}. PLPDP provides an important local alternative: it derives a time-varying inter-beat interval and a confidence signal from predominant local pulse (PLP) evidence, replacing a single global target with locally conditioned dynamic programming \cite{chiu2023localperiodicity}. However, pulse strength does not directly quantify whether one period is decisively preferred over competing half- or double-tempo explanations.

We propose CASM, a context-aware semi-Markov post-processor for compatible frozen activation models. CASM searches a sparse path over activation-supported peaks and estimates both a local period and its separation from the strongest competing period. These quantities centre and scale an event-to-event duration preference: clear local evidence permits decisive rhythmic correction, whereas ambiguous evidence makes the path increasingly activation-led. This is a graded relaxation rather than an ambiguity-triggered switch to the direct peak-picking path (Direct); a separate beat-count safeguard can return Direct when the structured output is implausibly sparse or dense. Figure~\ref{fig:casm-examples} visualises these two operating regimes, and a beat-synchronous meter decoder then produces downbeats on the selected beat grid.

CASM is designed to make structured decoding portable, not parameter-free. Its validation-selected global constants define one evidence-to-constraint response law, while each recording's local activations determine the effective target period, tolerance, and stiffness at inference time. Thus, the same frozen configuration requires neither backbone retraining nor per-track BPM or meter settings in the evaluated setting. We evaluate this transfer across three frozen backbones and two datasets, and release the implementation and calibrated configuration for direct use.\footnote{Code and demo are available at \url{https://zhanh-he.github.io/casm-icassp2026-plot}.}
```

### Figure 1: replacement caption

```latex
\caption{Two held-out excerpts illustrating the input-conditioned behaviour of CASM on Beat This activations from SMC. A well-separated local period can support recovery of weak, activation-supported reference beats; when period hypotheses compete, the duration term relaxes and the CASM path coincides with Direct in this example. DBN and PLPDP traces are included for comparison. Reference annotations and reference IBI are shown only for interpretation and are not inputs to any decoder.}
```

### Related Work — three paragraphs

```latex
\section{Related Work}
\label{sec:related}

Structured post-processing turns framewise beat evidence into coherent event sequences. Dynamic programming balances event evidence against a tempo-derived interval preference \cite{ellis2007beattracking}; probabilistic beat-position models and CRFs provide alternative sequence formulations \cite{korzeniowski2014crf,fillon2015crf}, while resonating comb filters estimate periodicity to inform tracking \cite{bock2015combfilter}. DBNs remain an influential joint decoder because they model tempo, phase, and meter in one path \cite{krebs2015dbn,bock2016joint}. Semi-Markov state-space modelling has likewise been used for efficient causal rhythm tracking \cite{heydari2022semimarkov}. These approaches establish the value of structured decoding after an activation network, but commonly rely on globally specified timing behaviour.

The closest line of work is local-periodicity decoding. Predominant Local Pulse (PLP) represents time-varying pulse evidence \cite{grosche2011plp}, and PLPDP converts PLP peaks into a local inter-beat interval and a pulse-strength confidence that condition dynamic programming \cite{chiu2023localperiodicity}. Subsequent PLP work has explored causal and controllable operation \cite{meier2024realtime} as well as differentiable pulse estimation, where competing periods can attenuate the resulting pulse representation \cite{chiu2025dplp}. CASM therefore does not claim local periodicity or ambiguity handling in general as new. Its distinction is to use an explicit dominant-versus-competitor period margin to condition a sparse event-level duration model for frozen tracker activations.

Other approaches move the coherence problem into a specifically trained predictor or a different deployment setting. Post-processing-free neural trackers seek outputs that can be peak-picked directly \cite{chen2022postprocessingfree,foscarin2024beat}, while masked diffusion iteratively constructs coherent sequences with a modified and retrained predictor \cite{foscarin2026masked}. Particle-filter trackers target online inference, and user-driven methods adapt a tracker with additional annotations \cite{hainsworth2004particle,heydari2021beatnet,pinto2021userdriven,maia2024selective}. CASM instead retains a frozen backbone and provides a deterministic plug-in decoder, with local structure used only when the activation evidence supports it.
```

## Why this option works

- It uses the strictest terminology: ``validation-selected,'' ``frozen,'' and ``compatible frozen activation models,'' rather than parameter-free, tuning-free, or universally model-agnostic.
- It gives the requested high-level explanation in an auditable form: a low-dimensional global response policy induces many input-derived, edge-wise local constraints. It does not say that CASM has an intrinsically superior calibration property.
- It says that a DBN's state support and transition assumptions are globally specified, rather than incorrectly suggesting that DBNs do not adapt their latent tempo/phase path to observations.
- It is the most compact candidate while retaining the full PLP--PLPDP--dPLP lineage and a three-paragraph Related Work structure.
