# CASM Introduction P3–P4 Narrative for Jollibear

## Goal

The first two paragraphs already establish the paper-level problem:

1. Beat tracking still commonly needs **post-processing** because framewise activations do not guarantee a coherent beat sequence.
2. The core post-processing problem is **when and how strongly temporal regularity should constrain local activation evidence**.
3. Ellis DP, CRF, and DBN mainly realise this balance through predefined temporal assumptions or globally configured constraints.

The remaining two paragraphs should therefore tell a very specific progression:

**globally configured temporal assumptions → locally adaptive temporal constraints (PLPDP) → ambiguity-aware local adaptation (CASM).**

The key point is that CASM must **not** be presented as the first confidence-aware or locally adaptive post-processor, because PLPDP already has both concepts.

---

## What PLPDP already does

PLPDP explicitly derives two time-varying quantities from predominant local pulse (PLP):

- an estimated local IBI, \(\hat{\delta}(n)\);
- a local confidence, \(\lambda(n)\).

The PLPDP paper treats PLP peak height as a confidence measure and defines \(\lambda(n)\) from the average heights of neighbouring PLP peaks. In its DP objective, \(\hat{\delta}(n)\) replaces the fixed target IBI and \(\lambda(n)\) replaces the fixed weight on the tempo-consistency penalty.

Therefore, we should **not** claim any of the following:

- CASM is the first method to use local confidence.
- PLPDP adapts only the local tempo but not the constraint strength.
- PLPDP uses a fixed-strength temporal prior.
- CASM is novel simply because it weakens the temporal constraint when confidence is low.

Those claims would be inaccurate.

---

## The most promising distinction

The potentially clean distinction is:

> **PLPDP confidence measures the strength/consistency of the selected local periodic structure, whereas CASM explicitly models ambiguity among competing periodic interpretations.**

This is not the same concept.

A local periodic cue may be strong while still being **ambiguous at the metrical level**. For example, half-tempo and double-tempo interpretations may both be well supported. A scalar confidence associated with one selected local period does not necessarily express how much support a competing period receives.

This distinction is especially plausible because the PLPDP paper itself reports that post-processing trackers can switch between metric levels such as half, third, double, or triple tempo.

However, this wording should be verified against the exact CASM implementation. We should avoid saying that PLPDP "cannot represent ambiguity" unless the mathematical comparison supports that claim. The safer formulation is that PLPDP **does not explicitly represent competition among multiple periodic hypotheses in its DP condition**, whereas CASM may do so.

---

## Recommended Paragraph 3: PLPDP as the bridge

A safe current draft is:

> PLPDP~\cite{chiu2023localperiodicity} takes an important step towards locally adaptive post-processing. Rather than relying on a fixed global tempo condition, it derives a time-varying IBI and confidence from predominant local pulse (PLP), and uses them to adapt both the target and strength of the temporal constraint during dynamic programming. This establishes an important principle: temporal structure can be inferred from the activation evidence itself rather than specified entirely in advance. However, confidence in a selected local period is not necessarily the same as ambiguity among competing periodic interpretations. For example, half- and double-tempo hypotheses may receive similar local support, making strong commitment to a single period undesirable.

Narrative role:

- Sentence 1: PLPDP is an important positive predecessor, not a strawman.
- Sentence 2: state accurately what it already contributes.
- Sentence 3: extract the principle that CASM inherits.
- Sentence 4–5: introduce the remaining problem, **ambiguity**, without falsely denying PLPDP's confidence mechanism.

Do not call PLPDP merely a "more balanced alternative". That phrase is vague and hides the actual technical progression.

---

## Recommended Paragraph 4: CASM

A safe current draft is:

> We introduce CASM, a context-aware semi-Markov post-processor designed around this distinction. CASM constructs a sparse path over activation-supported beat candidates and estimates local periodicity together with its ambiguity. These estimates jointly control the target, strength, and tolerance of the segment-duration preference. When one periodic interpretation is clearly supported, CASM enforces local regularity strongly enough to recover weak but activation-supported beats; when competing interpretations receive similar support, it relaxes this preference and follows the neural evidence more closely. Fig.~\ref{fig:casm-examples} illustrates these two behaviours. A beat-count safeguard and beat-synchronous meter stage further stabilise the output. CASM is model-agnostic, requires no neural-network retraining, and is released as an open-source, pip-installable post-processor with an interface compatible with madmom.

Narrative role:

- Start with **post-processor**, matching the title and the terminology of Paragraphs 1–3.
- Mention "semi-Markov" as the mechanism, not as the top-level problem definition.
- The key novelty should be the **decision about when local periodic structure is sufficiently unambiguous to impose strongly**.
- The clear/ambiguous two-case explanation should correspond directly to Fig. 1.
- Engineering properties such as model-agnostic, no retraining, pip-installable, and madmom-compatible should be compressed into the end of this paragraph rather than expanded into a separate contribution list unless space permits.

---

## Questions Jollibear should verify

### 1. What exactly is CASM's ambiguity quantity?

We need the mathematical definition.

- Is it based on the ratio/margin between the best and second-best local period?
- Is it based on a distribution over several period candidates?
- Does it explicitly include octave/metrical relations such as \(T/2\), \(T\), and \(2T\)?
- Is it an entropy-like quantity, a peak-ratio quantity, or something else?

This determines whether we can safely write **"ambiguity among competing periodic hypotheses"**.

### 2. How is CASM fundamentally different from PLPDP confidence?

PLPDP:
- local target IBI: \(\hat{\delta}(n)\);
- local confidence: \(\lambda(n)\);
- confidence is derived from PLP peak height;
- \(\lambda(n)\) directly scales the temporal penalty.

We need one precise sentence explaining what CASM adds beyond this.

A promising version, if mathematically correct, is:

> PLPDP adapts the temporal constraint according to the strength of the predominant local pulse, whereas CASM additionally considers whether that local periodicity has a uniquely supported interpretation.

But this should only be used if the implementation supports it.

### 3. Does CASM really adapt all three: target, strength, and tolerance?

The current manuscript says that local estimates control:

- target;
- strength;
- tolerance.

Please identify the exact equations/variables for each one.

If only two are truly adaptive, the Introduction should not claim three.

### 4. What does CASM do under high ambiguity?

We need to distinguish between:

- completely reverting to the Direct path;
- reducing the temporal prior;
- broadening the duration tolerance;
- selecting a different candidate set;
- some combination of these.

The phrase **"lets the neural activations dominate"** is safe only if this is really what the optimisation does.

### 5. Does CASM explicitly reason over multiple periodic hypotheses?

This is probably the strongest possible distinction from PLPDP.

If CASM retains several period candidates and evaluates their relative support, say so clearly.

If CASM instead computes only a scalar ambiguity measure from the same dominant period, then the Introduction should use the weaker wording:

> estimates local periodicity together with a measure of how reliable that estimate is.

### 6. How should metric-level ambiguity be described?

PLPDP itself reports metric-level switching among half-, third-, double-, and triple-tempo interpretations.

Please check whether CASM's ambiguity mechanism was specifically designed to address this phenomenon or whether half/double tempo is merely an illustrative example.

Do not imply a direct solution to metric-level switching unless supported experimentally or algorithmically.

### 7. Is "semi-Markov" essential to the novelty story?

We should be able to explain why the semi-Markov formulation matters beyond naming the model class.

Possible role:

- candidate-to-candidate segments directly represent inter-beat durations;
- duration preferences can therefore be made context dependent;
- this permits local control of target, strength, and tolerance.

If this is the real advantage, it should appear in Method and possibly as one compact clause in the Introduction.

### 8. Does CASM require future context?

Clarify whether local periodicity/ambiguity computation uses symmetric windows or future frames.

This determines whether CASM should be described strictly as an offline post-processor or whether an online variant is possible.

---

## Terminology rule for the Introduction

Use the following hierarchy consistently:

- **post-processing**: the stage/problem studied by the paper;
- **post-processor**: CASM, DBN, PLPDP, etc.;
- **temporal constraint / temporal preference / temporal regularity**: what the post-processor imposes;
- **semi-Markov formulation / search / decoding**: the computational mechanism.

Avoid repeatedly alternating among "structured decoder", "decoder", "decoding", and "post-processor". The title says **Post-Processor**, so that should remain the dominant term in the Introduction.

A good progression is:

> post-processing problem → predefined temporal constraints → locally adaptive post-processing → ambiguity-aware CASM → semi-Markov implementation.

---

## Claims to avoid until verified

1. "CASM is the first confidence-aware post-processor."
2. "PLPDP does not adapt the strength of its temporal prior."
3. "PLPDP only estimates local tempo."
4. "PLPDP cannot handle ambiguity."
5. "CASM solves metric-level switching."
6. "CASM always falls back to Direct under ambiguity."
7. "CASM requires less tuning than DBN" unless the calibration experiments directly support this claim.
8. "The current configuration generalises well on the MIREX benchmark" unless MIREX evaluation and the exact benchmark/protocol are clearly documented.

---

## One-sentence story

The strongest current story is:

> **Traditional post-processors impose globally configured temporal regularity; PLPDP makes that regularity locally adaptive using periodicity and confidence; CASM goes one step further by deciding how strongly to impose local regularity according to whether the local periodic evidence supports a sufficiently unambiguous interpretation.**

This final step is the part that should be checked carefully against the CASM equations before the Introduction is finalised.
