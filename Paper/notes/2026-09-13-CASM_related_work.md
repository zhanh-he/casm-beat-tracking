# CASM Related Work

## Copy-ready LaTeX

The following version is deliberately limited to two paragraphs. It contains no semi-Markov derivation and is intended to replace the current longer Related Work section.

```latex
\section{Related Work}
\label{sec:related}

Beat-tracking post-processors turn framewise evidence into coherent event sequences. Dynamic programming balances onset strength against a tempo-derived inter-beat prior \cite{ellis2007beattracking}; CRFs and comb filters add probabilistic event extraction or explicit periodicity estimates \cite{korzeniowski2014crf,bock2015combfilter}. DBNs became the standard joint decoder by modelling tempo, phase, and meter in a globally consistent beat/downbeat path \cite{krebs2015dbn,bock2016joint}. Semi-Markov models have also compressed the state space for efficient causal joint rhythm tracking \cite{heydari2022semimarkov}. These methods encode temporal assumptions outside the activation network. Conversely, post-processing-free systems train predictors to shoulder more temporal modelling \cite{chen2022postprocessingfree,foscarin2024beat}. Beat This! pairs strong F1 with minimal peak picking but exposes weaker continuity, whereas masked diffusion models competing grids through iterative neural inference \cite{foscarin2026masked}. These alternatives require specific predictor training; CASM is a deterministic plug-in for frozen outputs.

The closest line is local periodicity-based decoding. Predominant Local Pulse (PLP) estimates a time-varying pulse from a novelty or activation function \cite{grosche2011plp}. PLPDP converts PLP peaks into a local inter-beat interval and pulse-strength confidence, which replace the fixed tempo target and modulate the dynamic-programming penalty \cite{chiu2023localperiodicity}. Thus PLPDP already relaxes structure when confidence is low, but absolute pulse strength does not measure separation between competing periods. Subsequent work made PLP causal and controllable \cite{meier2024realtime}, while dPLP uses a softmax mixture whose interference suppresses periodic peaks when periods compete \cite{chiu2025dplp}. CASM therefore does not claim ambiguity handling itself as new. Instead, it uses the top-versus-competitor margin to control both the strength and tolerance of a sparse event-to-event duration cost, alongside a separate event-count safeguard that can return Direct. It also decodes downbeats on the selected beat grid without retraining.
```

## Length and citation checklist

- Main text: approximately 265 words, two paragraphs.
- New or easily missed keys: `grosche2011plp`, `meier2024realtime`, `chiu2025dplp`, and `foscarin2026masked`.
- Keep `heydari2022semimarkov` even though the semi-Markov mechanics move to Methodology. The citation prevents the paper from appearing to claim that semi-Markov rhythm tracking itself is new.
- If another 25 to 35 words must be removed, delete the CRF/comb-filter clause and its two citations before shortening the PLP lineage.
