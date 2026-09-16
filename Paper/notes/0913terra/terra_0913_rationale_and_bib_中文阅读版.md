# terra 的编辑 rationale、proofread 说明与 BibTeX 包（中文阅读版）

> **terra** 制作，2026-09-13。  
> 对应英文原件：`terra_0913_rationale_and_bib.md`。BibTeX 条目保持原样，英文稿中的 LaTex 句子仍应以英文原件为准。

## 一句话建议

优先以 **Option A** 为起点：它在功能性开头、准确的 DBN → PLPDP 桥接、不重复图~1、以及独立的 deployment 收尾之间最平衡。若你希望开头更自然、对一般读者更友好，选 **Option B**；若篇幅或证据边界最优先，选 **Option C**。

## 中文决策摘要

- 四段 Introduction 的节奏应是：**任务是什么** → **DBN 的全局约束与 PLPDP 的局部条件化** → **CASM 的机制与图~1** → **可部署性、一次 calibration、代码配置公开**。
- 三段 Related Work 的节奏应是：**structured decoding 的历史** → **PLP--PLPDP--dPLP 的最近谱系** → **online、adaptation、post-processing-free、diffusion 等不同部署路线**。
- PLPDP 在 Introduction 中只承担动机桥梁；在 Related Work 再完整写 local IBI、pulse-strength confidence、Real-Time PLP 和 dPLP。这样两节不会反复说同一句话。
- CASM 不应被描述为“第一个 ambiguity-aware decoder”。更准确的贡献组合是：top-versus-runner-up period margin、稀疏 event-level path、时长代价强度与容忍度的联调，以及与 margin 分离的 count safeguard。
- 图~1 不应再复述 left/right；caption 应说明两种行为、DBN/PLPDP traces 的比较角色，以及 reference annotations/IBI 只用于解释。

## 为什么采用四段 Introduction 与三段 Related Work

| 位置 | 该段唯一要完成的工作 | 刻意不重复的内容 |
| --- | --- | --- |
| Introduction ¶1 | 定义 beat/downbeat tracking 的用途，以及局部峰不足以直接形成可用节拍网格。 | DBN、PLPDP、结果与 F1。 |
| Introduction ¶2 | 从 DBN 的全局 timing assumption 过渡到 PLPDP 的 local evidence conditioning，并引出 competitor separation 的缺口。 | PLP 谱系细节、dPLP、CASM 公式。 |
| Introduction ¶3 | CASM 的 sparse path、margin-based graded relaxation、独立 count safeguard，以及一句图~1解释。 | 面板左/右叙述、部署承诺。 |
| Introduction ¶4 | frozen configuration、无逐曲 BPM/meter setting、可迁移性的机制解释与发布信息。 | 指标数字或强泛化结论。 |
| Related Work ¶1 | DP、beat-position model、comb filter、DBN、既有 semi-Markov rhythm tracking 的历史坐标。 | 再讲一次问题动机。 |
| Related Work ¶2 | PLP、PLPDP、Real-Time PLP、dPLP 与 CASM 的严格边界。 | 再讲一次 DBN 的失配情形。 |
| Related Work ¶3 | 其他方法为何服务于不同的 deployment setting。 | 再推导 CASM 的方法。 |

这套分工的核心是：Introduction 用 PLPDP 解释“为何需要 CASM”，Related Work 用 PLPDP 证明“CASM 在历史上究竟位于哪里”。

## 对 `casm_v4.tex` 的关键 proofread 修正

1. **开头口径：**Beat This、PLPDP、BeatMamba、BeatFM、HingeNet 等论文都先用普通读者能理解的方式定义 beat tracking，再讲技术管线。现稿以 “Despite recent attempts ...” 开头，默认读者已关心 DBN，不适合你希望的 functional opening；同时 Introduction 不应以 F1 开场或收尾。

2. **DBN 口径：**DBN 会基于观测推断 tempo/phase/meter trajectory，因此不能写成“DBN 不适应输入”。准确对比是：DBN 在 globally specified state support 和 transition behavior 下推断；CASM 则额外让 segment-duration potential 本身由 local activation context 条件化。

3. **PLPDP 口径：**PLPDP 不是 fixed-period method，也不是一个没有不确定性机制的 baseline。它把 PLP peak 的间隔和高度分别转为 local IBI 与 pulse-strength confidence，再进入 DP。CASM 的 margin 衡量的则是领先周期与竞争周期的**分离度**。

4. **PLP 后续工作：**Real-Time PLP 和 dPLP 是 PLP representation 的后续分支，并不是 PLPDP decoder 的直接续作。前者强调 causal/controllable operation，后者使 period selection 可微。

5. **ambiguity 与 Direct：**low margin 会逐步减弱、放宽 duration preference；它不会直接触发 Direct。精确返回 Direct 的条件是独立的 count-ratio safeguard。

6. **图~1：**现稿正文和 caption 都讲 left/right，属于重复；新的文案去掉这一层。图中 DBN/PLPDP trace 应说明是 comparison trace；reference annotations/IBI 应说明不是 decoder input。另建议把图上较宣传性的 `Mechanism-visible improvement` 改成更中性的 `Clear local period` 或 `Separated local periodicity supports correction`。也请检查 Methodology 的 `g(c)` 与 Fig.~2 caption 中 `w(c)` 是否一致。

## Calibration 与 generalisation：可以强讲、但必须讲对的高层逻辑

可以使用下述解释：

> CASM 并没有消除 calibration。其全局常数在 development data 上选择一次后冻结，作用是定义一条 evidence-to-constraint response law。推断时，每个 candidate transition 都从局部 activation context 得到自己的 target period 和 effective duration stiffness。因此，同一组低维全局 policy 参数会产生许多 input-dependent local constraint，而不是在每首录音上施加同一种有效 timing rigidity。

这很好地解释了为何 CASM **可能**需要较少的逐曲人工重调，以及为何固定配置可以在兼容 activation stream 上有可迁移性；但它不是“semi-Markov 天然不受 calibration 影响”的结论。

内部审计 `notes/2026-09-05_calibration_scale_scientific_audit.md` 指出：目前 CASM/DBN 的 calibration population、样本规模、selection objective、search policy 和 tempo-support choice 都不完全匹配。因此，在 Abstract/Introduction 中不要写：

- `CASM is less sensitive than DBNs to calibration data.`
- `CASM generalises better because it is semi-Markov.`
- `CASM is parameter-free / tuning-free.`

更稳妥的英文写法是：

```latex
A single validation-selected configuration is frozen across the evaluated backbones and datasets.
```

```latex
We analyse the sensitivity of decoder selection to development-set composition under the evaluated protocol.
```

若 Results 必须描述当前对照，最准确的是：

```latex
Under the current, different calibration procedures and search spaces, the selected CASM configurations show a narrower descriptive spread on the fixed evaluation panels than the selected DBN configurations.
```

## 三个 Option 的取舍

| 版本 | 适用情形 | 代价 |
| --- | --- | --- |
| A — balanced | 想要标准 ICASSP narrative，并完整解释 portability mechanism。 | 三版中相对最长。 |
| B — reader-first | 想让第一段格外易读、自然。 | 叙事性略强，稍占篇幅。 |
| C — compact/safe | 想最大程度避免 calibration 与 frozen-model claim 被 reviewer 抓住。 | 语气稍干、更技术化。 |

## Citation inventory 与 BibTeX

当前 `casm.bib` 中，三版文案新增使用但**唯一缺少**的 key 是 `grosche2011plp`。加入：

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

下面三条 PLP 谱系文献已存在于当前 `casm.bib`；为便于复制到别的 bib 文件，也保留完整条目：

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

其他所需 key 已在当前 `casm.bib`：

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
grosche2011plp                 % 需要补入
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

`foscarin2026masked` 已在当前 bib。投稿前请再次核对其会议状态和页码：

```bibtex
@InProceedings{foscarin2026masked,
  author    = {Foscarin, Francesco and Korzeniowski, Filip and Vogl, Richard},
  title     = {Masked Diffusion Enables Coherent Beat Tracking},
  booktitle = {Proceedings of the International Society for Music Information Retrieval Conference},
  year      = {2026},
  note      = {Proceedings pagination pending; arXiv:2608.04624}
}
```

## 实施备注

英文草案把 code/demo 的 footnote 放在 Introduction 最后一段，因为那里提出了“ready to use”的 deployment claim。若 Abstract 中仍保留现有 URL footnote，正文中只保留一处 URL，避免重复脚注。
