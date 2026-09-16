# terra's editorial rationale, proofread notes, and BibTeX packet

> Prepared by **terra** on 2026-09-13.  
> Companion to `terra_0913_option_A_balanced.md`, `terra_0913_option_B_reader_first.md`, and `terra_0913_option_C_compact_safe.md`.

## Recommendation in one line

Use **Option A** as the starting point. It is the best balance of a readable, functional opening; an accurate DBN → PLPDP bridge; a non-redundant Fig.~1 explanation; and a separate deployment conclusion. Choose **Option B** if you want a warmer, more human-facing first paragraph, or **Option C** if page budget and scientific defensibility are the overriding priorities.

## 中文决策摘要

- 我建议先用 **A**：第一段是 functional/general 的 beat tracking 定义，第二段才进入 DBN → PLPDP，因此读者不会一开场就被后处理术语淹没。
- PLPDP 在 Introduction 只承担“从全局约束走向 local evidence conditioning”的桥梁角色；在 Related Work 才完整写 PLP、local IBI、pulse-strength confidence、Real-Time PLP 与 dPLP，避免同一句话说两遍。
- CASM 的新意不能写成“第一次处理 ambiguity”。更准确的是：用 top-versus-runner-up margin 驱动稀疏 event path 的 duration cost，并同时改变刚性与容忍度；count safeguard 是与 margin 分离的安全阀。
- Fig.~1 文案不再重复 left/right，而是说明两种 operating regime；caption 同时解释 DBN/PLPDP traces 与 reference IBI 的角色。
- “less sensitive than DBNs to calibration data”目前证据不够干净。文案保留你想要的高层机制解释——同一套全局常数是 input-conditioned response law——但不把它写成已经被严格因果证明的泛化结论。

## The division of labour: why four Introduction paragraphs and three Related Work paragraphs

| Location | Job | What it deliberately does not repeat |
| --- | --- | --- |
| Introduction ¶1 | What beat/downbeat tracking produces, why an ordered event grid matters, and why isolated peaks are insufficient. | DBNs, PLPDP, results, F1. |
| Introduction ¶2 | The actual problem: global DBN assumptions versus activation-conditioned local periodicity; introduce PLPDP once as the nearest conceptual bridge. | PLPDP's full lineage, dPLP, or CASM's formula. |
| Introduction ¶3 | What CASM does differently, including graded margin-based relaxation, the separate count safeguard, and the one-sentence Fig.~1 explanation. | “left/right” panel narration and deployment claims. |
| Introduction ¶4 | The contribution/deployment contract: one validation-selected configuration, frozen inference, no per-track BPM/meter setting, code/configuration release. | Any raw F1/CMLt/AMLt claim. |
| Related Work ¶1 | Historical structured-decoding map: DP, probabilistic event extraction, comb filters, DBNs, and prior semi-Markov rhythm tracking. | The Introduction's problem framing. |
| Related Work ¶2 | The close PLP → PLPDP → Real-Time PLP/dPLP lineage and the exact novelty boundary. | A second generic explanation of why DBNs can fail. |
| Related Work ¶3 | Other deployment choices: online filtering, target adaptation, post-processing-free predictors, and diffusion. | Repeating CASM's mechanism. |

This layout preserves the useful PLPDP/local-evidence discussion, but gives it two different purposes: **motivation** in the Introduction, and **historical/technical positioning** in Related Work.

## What was proofread and corrected from `casm_v4.tex`

1. **Opening register.** The present opening starts with a reaction to DBN removal. The reading set (especially PLPDP, BeatMamba, BeatFM, and HingeNet) instead begins with the beat as a useful temporal pulse, then introduces system details. All three options follow that convention and contain no F1 claim in the opening or closing paragraph.

2. **DBN wording.** A DBN does infer a tempo/phase/meter trajectory from its observations. The accurate contrast is not “CASM adapts, DBN does not,” but: DBNs infer under globally specified state support and transition behaviour, whereas CASM additionally conditions its segment-duration potential on local activation-derived context.

3. **PLPDP wording.** PLPDP is not a fixed-period decoder and it is not merely a weak baseline. It derives a local IBI target and a pulse-strength confidence from PLP, then uses both in DP. CASM's defensible distinction is that its margin measures **leading-versus-competing period separation**, and controls both stiffness and tolerance of an event-level cost.

4. **PLP descendants.** `Real-Time PLP` and `dPLP` are subsequent branches of the PLP representation, not direct continuations of the PLPDP decoder. The former focuses on causal/controllable operation; the latter makes period selection differentiable.

5. **Ambiguity versus Direct.** Low CASM margin gradually weakens and broadens the duration preference. It does **not** directly switch to Direct. Exact return to Direct is the separate count-ratio safeguard. The prose and Fig.~1 captions now make that distinction explicit.

6. **Figure 1.** The current prose and caption each narrate “left/right,” although the graphic titles already do so. The proposed captions describe the two regimes without that repetition. They also identify DBN/PLPDP as comparison traces and state that reference annotations/IBI are interpretive only, not decoder inputs.

7. **Small Figure 1 audit items to resolve in the source figure/Methodology.** The left heading “Mechanism-visible improvement” reads slightly promotional; `Clear local period` or `Separated local periodicity supports correction` is more neutral. Also check the notation mismatch between Methodology's `g(c)` and Fig.~2's `w(c)`.

## Calibration and generalisation: the safe high-level story

The requested conceptual explanation can be strong without overclaiming:

> CASM does not eliminate calibration. Its global constants are selected once on development data and then frozen. They specify an evidence-to-constraint response law. At inference, every candidate transition receives its own target period and effective duration stiffness from local activation context. The same low-dimensional global policy therefore produces many input-dependent local constraints, rather than imposing one effective timing rigidity on every recording.

This is the right explanation for why CASM may need less **manual per-track retuning** and why a frozen configuration can plausibly transfer across compatible activation streams. It is not a claim that semi-Markov models are inherently calibration-independent.

The internal calibration audit in `notes/2026-09-05_calibration_scale_scientific_audit.md` finds that the present CASM/DBN comparison is not fully matched: calibration population/size, selection objective, search policy, and tempo-support choices differ. Until that is controlled, avoid these strong formulations in the Abstract and Introduction:

- `CASM is less sensitive than DBNs to calibration data.`
- `CASM generalises better because it is semi-Markov.`
- `CASM is parameter-free / tuning-free.`

Prefer one of these instead:

```latex
A single validation-selected configuration is frozen across the evaluated backbones and datasets.
```

```latex
We analyse the sensitivity of decoder selection to development-set composition under the evaluated protocol.
```

For the Results section, if the comparison remains in the paper, the precise form is:

```latex
Under the current, different calibration procedures and search spaces, the selected CASM configurations show a narrower descriptive spread on the fixed evaluation panels than the selected DBN configurations.
```

## Option comparison

| Option | Best when | Trade-off |
| --- | --- | --- |
| A — balanced | You want the most conventional ICASSP story and enough room to explain the portability mechanism. | About the longest of the three. |
| B — reader-first | You want the first paragraph to be especially accessible and human-readable. | Slightly more narrative, hence marginally less compact. |
| C — compact/safe | You want the least contestable wording around calibration and frozen-model compatibility. | A little drier and more technically guarded. |

## Citation inventory

### Newly required key

The current `casm.bib` already contains the other keys used in these drafts. The one missing key is `grosche2011plp`; add this entry:

```bibtex
@Article{grosche2011plp,
  author  = {Grosche, Peter and M{\"u}ller, Meinard},
  title   = {Extracting Predominant Local Pulse Information from Music Recordings},
  journal = {IEEE Transactions on Audio, Speech, and Language Processing},
  volume  = {19},
  number  = {6},
  pages   = {1688--1701},
  year    = {2011},
  doi     = {10.1109/TASL.2010.2096216}
}
```

### PLP-lineage entries (complete copyable packet)

These three are already present in the current `casm.bib`; they are included here so the PLP lineage can be copied into another bibliography without hunting for them.

```bibtex
@Article{chiu2023localperiodicity,
  author  = {Chiu, Ching-Yu and M{\"u}ller, Meinard and Davies, Matthew E. P. and Su, Alvin Wen-Yu and Yang, Yi-Hsuan},
  title   = {Local Periodicity-Based Beat Tracking for Expressive Classical Piano Music},
  journal = {IEEE/ACM Transactions on Audio, Speech, and Language Processing},
  volume  = {31},
  pages   = {2824--2835},
  year    = {2023},
  doi     = {10.1109/TASLP.2023.3297956}
}

@Article{meier2024realtime,
  author  = {Meier, Peter and Chiu, Ching-Yu and M{\"u}ller, Meinard},
  title   = {A Real-Time Beat Tracking System with Zero Latency and Enhanced Controllability},
  journal = {Transactions of the International Society for Music Information Retrieval},
  volume  = {7},
  number  = {1},
  pages   = {213--227},
  year    = {2024},
  doi     = {10.5334/tismir.189}
}

@InProceedings{chiu2025dplp,
  author    = {Chiu, Ching-Yu and Strahl, Sebastian and M{\"u}ller, Meinard},
  title     = {{dPLP}: A Differentiable Version of Predominant Local Pulse Estimation},
  booktitle = {Proceedings of the International Society for Music Information Retrieval Conference},
  pages     = {198--205},
  year      = {2025},
  doi       = {10.5281/zenodo.17811352}
}
```

### Other keys used by the recommended Option A

All are already present in the current `casm.bib`:

```text
ahn2026smcblindspot
bock2015combfilter
bock2016joint
chen2022postprocessingfree
chiu2023localperiodicity
chiu2025dplp
ellis2007beattracking
fillon2015crf
foscarin2024beat
foscarin2026masked
grosche2011plp                 % add this one
hainsworth2004particle
heydari2021beatnet
heydari2022semimarkov
heydari2024beatnetplus
korzeniowski2014crf
krebs2015dbn
maia2022adapting
meier2024realtime
pinto2021userdriven
```

### Optional standalone entry for the third Related Work paragraph

`foscarin2026masked` is already in the current file. Its venue status should be checked again just before submission, because proceedings pagination may change:

```bibtex
@InProceedings{foscarin2026masked,
  author    = {Foscarin, Francesco and Korzeniowski, Filip and Vogl, Richard},
  title     = {Masked Diffusion Enables Coherent Beat Tracking},
  booktitle = {Proceedings of the International Society for Music Information Retrieval Conference},
  year      = {2026},
  note      = {Proceedings pagination pending; arXiv:2608.04624}
}
```

## Implementation note

The proposed code places the availability footnote in the final Introduction paragraph because that is where the “ready to use” claim is made. If the existing Abstract footnote remains, retain the URL in **one** location only to avoid an unnecessary duplicate footnote.
