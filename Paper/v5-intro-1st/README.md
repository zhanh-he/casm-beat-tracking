# CASM v5 alternatives

This directory is an isolated revision workspace derived from
`Paper/main/casm_v4.tex`.  It intentionally does not modify `Paper/main` or the
other concurrently produced v5 directories.

## Files

- `casm_v5a.tex` / `casm_v5a.pdf` — balanced, reviewer-facing version.  It gives
  the fullest DBN → PLPDP → causal/online alternatives → CASM lineage.
- `casm_v5b.tex` / `casm_v5b.pdf` — compact ICASSP version.  It preserves the
  required novelty boundaries with the smallest Introduction.
- `casm_v5c.tex` / `casm_v5c.pdf` — concept-led version.  It organizes the
  Introduction around when rhythmic structure has earned enough trust to
  override local neural evidence.

My default recommendation is **v5a** for technical completeness.  Choose v5b if
space is the dominant constraint, or v5c if a more memorable conceptual opening
is preferred.

## Changes shared by all three versions

1. The standalone Related Work section has been removed and its essential
   literature positioning has been integrated into the Introduction.
2. The former Methodology overview has moved into the Introduction at a high
   level.  The longer mechanism description formerly in the Introduction now
   opens the CASM Overview subsection in Methodology.
3. Both mechanism figures now serve Methodology: the activation examples follow
   the overview, and the response-law figure follows the duration-cost equation
   and explanation.
4. The literature boundary now states explicitly that DBN paths are
   observation-dependent even though their support and transition assumptions
   are globally configured; PLPDP already uses a local IBI and confidence; and
   the 1D semi-Markov model and BeatNet/BeatNet+ are causal or real-time systems,
   whereas CASM is an offline sparse candidate-to-candidate decoder for frozen
   activation streams.
5. The ambiguous example is described as a soft weakening of the duration term,
   not as an ambiguity-triggered switch to Direct.  The exact Direct return is a
   separate count-ratio safeguard.
6. The response coefficient is consistently denoted by `w(c)` in the text,
   equation, and Figure 2.
7. Each Introduction ends with an explicit novelty-and-effectiveness contribution
   sentence.  Claims about calibration sensitivity are protocol-qualified.

All three PDFs compile successfully with bundled Tectonic and contain five pages.
