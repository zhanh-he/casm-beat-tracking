# CASM Introduction + Related Work — Option B: reader-first, more narrative

> Prepared by **terra** on 2026-09-13.  
> Intended use: choose this if you want the opening to feel closer to the plain functional introductions in BeatMamba, BeatFM, HingeNet, and PLPDP before moving into the decoding argument.

## Copy-ready LaTeX

### Introduction — four paragraphs

```latex
\section{Introduction}
\label{sec:intro}

Beat tracking gives a music system a sense of where a performance is in time. By finding the repeating pulse that listeners naturally follow, it provides a temporal reference for transcription, structural analysis, score--audio alignment, and tools that respond in synchrony with music. Yet this pulse is not always marked by an obvious sound: a performer may slow down or speed up, an instrument may enter softly, and a dense passage may suggest more than one plausible pulse. Listeners can use the surrounding musical context to keep a sense of pulse; current neural trackers may instead follow a compelling local cue into the wrong tempo or beat rate \cite{chiu2023localperiodicity,ru2026beatmamba,ahn2026smcblindspot,foscarin2026masked}.

The decoder must therefore decide how much to trust local activation evidence and how much temporal regularity to impose. DBNs make that decision through a global state model over tempo, phase, and meter \cite{krebs2015dbn,bock2016joint}. The model is valuable when its tempo range, metrical inventory, and transition behaviour agree with the music, but those assumptions can become restrictive for unusual tempi, changing meter, or expressive timing \cite{chiu2023localperiodicity,ahn2026smcblindspot}. PLPDP makes the temporal expectation more local: predominant local pulse evidence yields a time-varying inter-beat interval and a confidence that modulates dynamic programming \cite{chiu2023localperiodicity}. This is an important precedent for using activation-derived context in decoding. Still, selecting the strongest local period does not reveal whether it is clearly better than a competing half- or double-period interpretation.

We propose \emph{Context-Aware Semi-Markov} (CASM) decoding to make that distinction explicit. CASM searches a sparse graph of activation-supported candidates rather than every frame. For each candidate, it estimates a local period and a margin between the best period hypothesis and its closest competitor. A large margin makes the duration preference precise and influential, so that CASM can use clear periodicity to bridge a weak but supported beat. A small margin makes the preference broader and weaker, preventing a doubtful period from overriding the neural evidence. Its count safeguard is separate from this local response: only an implausibly sparse or dense structured path is replaced by Direct. Figure~\ref{fig:casm-examples} contrasts the two outcomes without requiring a special ambiguity router.

The result is a transparent plug-in post-processor for compatible activations from an already trained tracker. CASM has one validation-selected global configuration, but its effective constraint is recomputed from each recording: the constants describe how to react to local evidence, not a fixed BPM, meter, or tempo rigidity for every input. This gives a high-level reason to expect less manual retuning when the activation stream or musical material changes, while keeping the claim testable rather than treating it as a property of semi-Markov decoding itself. We evaluate this setting across frozen backbones and datasets, and release the code, examples, and ready-to-use configuration.\footnote{Code and demo are available at \url{https://zhanh-he.github.io/casm-icassp2026-plot}.}
```

### Figure 1: replacement caption

```latex
\caption{Two held-out excerpts illustrating the input-conditioned behaviour of CASM on Beat This activations from SMC. A well-separated local period can support recovery of weak, activation-supported reference beats; when period hypotheses compete, the duration term relaxes and the CASM path coincides with Direct in this example. DBN and PLPDP traces are included for comparison. Reference annotations and reference IBI are shown only for interpretation and are not inputs to any decoder.}
```

### Related Work — three paragraphs

```latex
\section{Related Work}
\label{sec:related}

The post-processing problem predates neural beat activations. Early dynamic-programming trackers formalised the trade-off between local onset evidence and approximately regular inter-beat intervals \cite{ellis2007beattracking}. Probabilistic beat-position extraction \cite{korzeniowski2014crf} and resonating comb filters \cite{bock2015combfilter} offered different ways to make periodic structure explicit. DBNs subsequently provided a practical joint beat/downbeat formulation by decoding tempo, phase, and meter together \cite{krebs2015dbn,bock2016joint}. Related one-dimensional semi-Markov state spaces reduce the cost of causal joint rhythm inference \cite{heydari2022semimarkov}. CASM belongs to this broad family of explicit sequence decoders, but it uses a sparse event graph and an input-conditioned duration potential rather than a fixed state-space transition law.

PLP is the most direct conceptual predecessor. It extracts a locally dominant, time-varying pulse from novelty or activation evidence \cite{grosche2011plp}. Building on that representation, PLPDP converts PLP peaks into a local IBI trajectory and pulse-strength confidence and injects both into framewise dynamic programming \cite{chiu2023localperiodicity}. Hence PLPDP already adapts its temporal constraint when local evidence is weak; CASM should not be framed as merely adding ``confidence.'' The distinction is what the quantity measures: CASM's margin compares the selected period with its strongest competitor, and it changes both duration-cost stiffness and tolerance on an event-to-event path. Later PLP work studies causal controllable estimation \cite{meier2024realtime} and differentiable soft mixtures of competing period kernels \cite{chiu2025dplp}. These works make the lineage clear while delimiting the narrower contribution of CASM.

Recent work also attacks incoherent activations before or outside a plug-in decoder. Online particle-filter systems infer rhythm states causally \cite{hainsworth2004particle,heydari2021beatnet}, and annotation-driven methods adapt a tracker to a target use case \cite{pinto2021userdriven,maia2022adapting}. Post-processing-free networks learn to carry more temporal structure in the predictor \cite{chen2022postprocessingfree,foscarin2024beat}; masked diffusion learns an iterative mechanism for selecting a coherent beat grid from competing outputs \cite{foscarin2026masked}. CASM makes a complementary deployment choice: it leaves the predictor unchanged, consumes its frozen activations, and adds deterministic beat decoding followed by beat-synchronous downbeat decoding.
```

## Why this option works

- The first two sentences can be read by a broad MIR audience without first knowing what a DBN or an activation decoder is.
- The central sentence is a clear human-level formulation of the paper's tension: *how much should decoding trust evidence versus regularity?*
- The CASM paragraph deliberately separates soft local relaxation from the hard count fallback, preventing the common but inaccurate statement that ambiguity itself switches CASM to Direct.
- The closing paragraph gives the requested high-level portability rationale while explicitly avoiding a causal claim that the current calibration study cannot yet prove.
- In Related Work, the first paragraph ends with CASM's family membership, the second handles the close PLPDP comparison, and the third separates online/adaptive/retrained alternatives from the frozen-backbone deployment case.
