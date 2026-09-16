---
title: CASM related-work reading notes
date: 2026-09-09
tags: [beat-tracking, post-processing, PLP, PLPDP, semi-Markov, ambiguity]
---

# CASM 文献阅读笔记

## 结论先行

PLPDP 是 CASM 最接近的概念前身，应该在 Related Work 中拥有独立而明确的位置，而不是只作为一个实验 baseline 被顺带提及。它已经完成了两个关键动作：用局部 PLP 估计替代固定的全局节拍间隔，并用局部置信度调节动态规划中的节奏一致性惩罚。因此，不能把 PLPDP 描写成“无论是否可靠都强制同样的周期约束”。

CASM 与 PLPDP 的真正区别也不只是“ambiguity 高时退化到 Direct”。更准确的机制分成两层：局部周期 margin 低时，CASM 减弱并放宽 duration cost，使搜索更依赖神经激活；只有当最终结构化路径的事件数与 Direct 路径明显不一致时，独立的 count safeguard 才返回原始 Direct 结果。换言之，ambiguity 并不直接触发硬切换，Direct fallback 是另一个确定性安全检查。

dPLP 又使“ambiguity-aware”这一表述需要更谨慎。它不只选一个最强周期，而是对多个周期核做 softmax 加权；当多个周期竞争时，核之间的干涉会削弱规则脉冲，使输出落在原始 novelty 与硬 PLP 之间。因而 CASM 不宜声称首次处理局部周期歧义。更可守的贡献是：显式使用最佳周期与最强竞争周期之间的 margin，并把它用于稀疏事件路径的约束强度和容忍度，同时保留能够精确返回 Direct 路径的安全阀。

## PLP 谱系与 CASM 的位置

| 方法 | 周期或不确定性信号 | 歧义时的行为 | 会否精确返回 Direct | 是否要求重训 backbone |
| --- | --- | --- | --- | --- |
| PLP | 局部 tempogram 中的主导周期 | 每个时刻硬选主导核，歧义通常被压成一个赢家 | 否 | 否 |
| PLPDP | PLP 峰值给出的局部 IBI；相邻 PLP 峰强度形成置信度 | 低置信度时减弱 DP 的 tempo-consistency penalty | 否。惩罚变弱不等于 Direct peak picking | 否 |
| Real-Time PLP | 因果 PLP、稳定性与 lookahead 信息 | 重点是实时性、零延迟和可控性，不是重新定义 PLPDP 解码 | 否 | 否 |
| dPLP | 对所有候选周期的 softmax 权重 | 多周期竞争产生干涉，减少不可靠的周期峰 | 否。作者描述为 novelty 与原始 PLP 之间的中间状态 | 可微，可并入端到端训练；论文仅作小规模 proof of concept |
| CASM | 最佳周期与最强竞争周期的归一化 margin | margin 低时同时减弱并放宽 duration cost | 可以，但由独立的事件数安全检查触发 | 否 |
| Masked diffusion | 对多个可能输出节拍网格的生成式建模 | 通过迭代推断形成一个连贯输出 | 否 | 是，需要专门训练或修改 predictor |

### “续作”关系需要怎样表述

- Real-Time PLP 是原始 PLP 的因果化和交互式应用分支。它与 PLPDP 共用局部脉冲思想，但并不是 PLPDP 动态规划解码器的直接升级版。
- dPLP 是 PLP 表示本身更直接的方法后续：把不可微的 argmax 主周期选择改为 softmax 加权。它同样不是在 PLPDP 的 DP 递推式上继续扩展。
- 因而论文里可以写 “subsequent PLP work”，不建议写 “subsequent extensions of PLPDP”。

## 核心论文精读

### 1. Grosche and Müller, PLP

**Meta**

- Peter Grosche and Meinard Müller, “Extracting Predominant Local Pulse Information from Music Recordings”.
- *IEEE Transactions on Audio, Speech, and Language Processing*, 19(6):1688–1701, 2011.
- DOI: 10.1109/TASL.2010.2096216.
- 原始资料：[作者机构书目信息](https://cris.fau.de/publications/224409325/)；[官方教程与实现说明](https://www.audiolabs-erlangen.de/resources/MIR/FMP/C6/C6S3_PredominantLocalPulse.html)。

**精简概述**

PLP 从 novelty function 的局部 tempogram 中选择显著周期，为每个时间位置构造相应的周期核，再通过 overlap-add 和整流得到局部脉冲表示。它不是完整的节拍序列解码器，而是一种能随时间改变 tempo 的中层表示。它解决的是“局部主导脉冲是什么”，没有显式比较多个竞争周期的可信间隔。

**对 CASM 的意义**

CASM 的局部自相关不是凭空出现的新方向，而是与 PLP 同属局部周期证据这一谱系。创新表述应落在如何量化竞争、如何作用到事件级结构搜索，以及何时保留 Direct，而不应落在“首次使用局部周期”。

### 2. Chiu et al., PLPDP

**Meta**

- Ching-Yu Chiu, Meinard Müller, Matthew E. P. Davies, Alvin Wen-Yu Su, and Yi-Hsuan Yang, “Local Periodicity-Based Beat Tracking for Expressive Classical Piano Music”.
- *IEEE/ACM Transactions on Audio, Speech, and Language Processing*, 31:2824–2835, 2023.
- DOI: 10.1109/TASLP.2023.3297956.
- 原始资料：[论文](https://mir.dei.uc.pt/pdf/Journals/MERGE/TASLP_2023_Chiu.pdf)；[官方代码](https://github.com/SunnyCYC/plpdp4beat)。

**精简概述**

PLPDP 面向表现性古典钢琴中明显的局部 tempo 变化。它先计算多时间尺度 PLP，再从 PLP 峰列构造随时间变化的目标 IBI 和置信度。DP 的 transition penalty 不再围绕单一全局 tempo，而是围绕局部 IBI；置信度则调节该惩罚的权重。作者在 Maz-5 和 ASAP 上用 madmom 激活以及合成 oracle 激活评估。Maz-5 的 F1 提升尤其明显，主要来自 recall 增益；ASAP 的提升较小。

**局限与边界**

论文自己指出，只要伪激活恰好符合局部周期，它仍可能被强化；反过来，真实但不符合所选局部周期的峰也可能被忽略。PLPDP 的 confidence 来自 PLP 脉冲强度，而不是第一、第二候选周期的可分性。因此，两个相近或倍半关系的周期都很强时，赢家仍可能有较高的绝对强度。

**对用户判断的修正**

PLPDP 确实会在低置信度时弱化结构约束，所以“CASM 唯一多了 ambiguity 高时退化”说得过宽。更精确的差异是 CASM 用竞争 margin 识别“没有决定性赢家”的情形；同时，CASM 的精确 Direct fallback 来自独立 count safeguard，而不是 margin 直接触发。

### 3. Meier et al., Real-Time PLP

**Meta**

- Peter Meier, Ching-Yu Chiu, and Meinard Müller, “A Real-Time Beat Tracking System with Zero Latency and Enhanced Controllability”.
- *Transactions of the International Society for Music Information Retrieval*, 7(1):213–227, 2024.
- DOI: 10.5334/tismir.189.
- 原始资料：[期刊论文](https://transactions.ismir.net/articles/10.5334/tismir.189)；[项目页、代码与演示](https://www.audiolabs-erlangen.de/resources/MIR/2024-TISMIR-RealTimePLP)。

**精简概述**

这项工作将 PLP 改造成因果、零延迟的实时节拍系统，并显式讨论 context length、输出稳定性、lookahead 和交互可控性。贡献重点是在线应用中的延迟与控制，而不是 PLPDP 的置信度设计，也不是 beat/downbeat 联合离线解码。

**对 CASM 的意义**

它适合用一句话说明 PLP 思想已经沿实时方向扩展。若篇幅紧张，它的优先级低于 PLPDP 和 dPLP，但仍有助于准确描述这条研究线的后续发展。

### 4. Chiu et al., dPLP

**Meta**

- Ching-Yu Chiu, Sebastian Strahl, and Meinard Müller, “dPLP: A Differentiable Version of Predominant Local Pulse Estimation”.
- *Proceedings of ISMIR*, pp. 198–205, 2025.
- 原始资料：[ISMIR 2025 目录](https://ismir.net/conferences/ismir-2025/)；[作者版论文](https://audiolabs-erlangen.de/content/05_fau/professor/00_mueller/03_publications/2025_ChiuSM_dPLP_ISMIR_ePrint.pdf)；[项目页](https://www.audiolabs-erlangen.de/resources/MIR/2025_ChiuSM_dPLP_ISMIR)。

**精简概述**

原始 PLP 在每个时间位置用 argmax 选一个主周期，这一步不可微，也会丢掉竞争周期信息。dPLP 对所有周期核做带温度的 softmax 加权，使整条 PLP 管线可微。在周期明确的区域，输出接近硬 PLP；在多个 tempo 候选竞争的区域，不同核的相位干涉会减少清晰峰值。作者把它解释为原始 novelty 与原始 PLP 之间的中间表示。

**实验边界**

论文是 proof of concept，使用 GTZAN popular-music 子集的 100 首曲目，并采用 60/20/20 切分。主要展示可微 PLP 能被训练，而不是证明一个完整 beat/downbeat decoder 的 SOTA 优势。因此，它削弱的是 CASM 对“ambiguity-aware”概念的宽泛新颖性，但不消除 CASM 作为冻结 backbone 的事件级 plug-in decoder 的差异。

### 5. Heydari et al., one-dimensional semi-Markov state space

**Meta**

- Mojtaba Heydari, Matthew McCallum, Andreas Ehmann, and Zhiyao Duan, “A Novel 1D State Space for Efficient Music Rhythmic Analysis”.
- *Proceedings of IEEE ICASSP*, pp. 421–425, 2022.
- 原始资料：[论文](https://arxiv.org/abs/2111.00704)；[作者代码](https://github.com/mjhydri/1D-StateSpace)。

**精简概述**

论文把常见二维 tempo-position 状态空间压缩为一维 semi-Markov 模型，用 jump-back reward 完成因果的 beat、downbeat、tempo 和 meter 联合跟踪。其主要贡献是状态空间和推断效率，在与联合在线模型相近的性能下报告超过 30 倍的加速。

**对 CASM 的意义**

这篇必须引用，否则标题中的 “Semi-Markov” 容易被理解成对 beat tracking 中 semi-Markov 建模本身的首创主张。两者的重点不同：该文是因果的一维隐状态后验推断和效率设计；CASM 是离线的稀疏候选事件路径，用局部 ambiguity 调节 segment duration cost。Related Work 只需一句交代先例，具体差异放 Methodology。

## 相邻研究的定向阅读

| 论文与 meta | 精简概述 | 与 CASM 的关系 |
| --- | --- | --- |
| Daniel P. W. Ellis, “Beat Tracking by Dynamic Programming”, *Journal of New Music Research*, 36(1):51–60, 2007, DOI 10.1080/09298210701653344. [作者项目页](https://www.ee.columbia.edu/~dpwe/LabROSA/matlab/beat_simple/) | 以全局 tempo 构造转移代价，用 DP 平衡 onset evidence 与近似规则的 IBI。论文也检查了固定目标 tempo 的局限。 | 是 PLPDP 和 CASM 都要对照的经典“证据项 + 时长先验”范式。 |
| Filip Korzeniowski, Sebastian Böck, and Gerhard Widmer, “Probabilistic Extraction of Beat Positions from a Beat Activation Function”, *ISMIR*, 2014. [论文](https://www.cp.jku.at/research/papers/Korzeniowski_ISMIR_2014.pdf) | 用条件随机场从神经 beat activation 中抽取节拍事件。 | 代表非 DBN 的概率序列解码；在两段式 Related Work 中只需一个并列短语。 |
| Sebastian Böck, Florian Krebs, and Gerhard Widmer, “Accurate Tempo Estimation Based on Recurrent Neural Networks and Resonating Comb Filters”, *ISMIR*, pp. 625–631, 2015. [论文](https://archives.ismir.net/ismir2015/paper/000196.pdf) | RNN 产生 beat-level 表示，resonating comb-filter bank 估计主导周期。它本身侧重全局 tempo，而非完整 beat/downbeat 序列。 | 可为实验中的 comb-filter 家族提供出处，但不应写成 joint beat/downbeat decoder。 |
| Florian Krebs, Sebastian Böck, and Gerhard Widmer, “An Efficient State-Space Model for Joint Tempo and Meter Tracking”, *ISMIR*, pp. 72–78, 2015. [论文](https://archives.ismir.net/ismir2015/paper/000239.pdf) | 改进 bar-pointer DBN 的状态离散化与 tempo transition，联合建模 bar position、tempo 和 meter，并显著降低时空复杂度。 | 是现代 joint beat/downbeat DBN 的核心结构来源，也是 CASM 反复比较的固定状态和转移假设代表。 |
| Sebastian Böck, Florian Krebs, and Gerhard Widmer, “Joint Beat and Downbeat Tracking with Recurrent Neural Networks”, *ISMIR*, pp. 255–261, 2016. [论文](https://archives.ismir.net/ismir2016/paper/000186.pdf) | RNN 预测 beat/downbeat activation，DBN 联合恢复 tempo、phase 和 meter。 | 奠定 neural activation + DBN 的标准管线。 |
| Tsung-Ping Chen and Li Su, “Toward Postprocessing-Free Neural Networks for Joint Beat and Downbeat Estimation”, *ISMIR*, pp. 27–35, 2022. [论文](https://archives.ismir.net/ismir2022/paper/000002.pdf) | 通过网络结构和损失重构，尝试让 joint beat/downbeat predictor 不依赖后处理。 | 代表把结构负担移回训练阶段的路线；CASM 则保持 predictor 冻结。 |
| Francesco Foscarin, Jan Schlüter, and Gerhard Widmer, “Beat This! Accurate Beat Tracking without DBN Postprocessing”, *ISMIR*, pp. 962–969, 2024. [论文](https://zenodo.org/record/14877491/files/000107.pdf)；[代码](https://github.com/CPJKU/beat_this) | 强化 predictor，使局部极大值和阈值即可产生很强 F1；附加 DBN 常改善 continuity，却可能因假设不合而改坏原本正确的输出。 | CASM 的 Direct 路径与 frozen-backbone setting 直接来自这一现实场景。CASM 试图在 F1 与 coherence 之间提供无需重训的中间选择。 |
| Francesco Foscarin, Filip Korzeniowski, and Richard Vogl, “Masked Diffusion Enables Coherent Beat Tracking”, accepted for *ISMIR*, 2026; arXiv:2608.04624. [论文](https://arxiv.org/abs/2608.04624)；[代码](https://github.com/fosfrancesco/md_beat_this) | 将不连贯输出归因于多个合理 beat grids 的混合，用 masked diffusion 和迭代推断生成连贯预测。 | 它已直接讨论 ambiguity 和多解，但需要修改并训练预测模型；CASM 的区别是固定 backbone、确定性后处理和透明回退。 |

## 写作可用的证据边界

### 可以较强地写

- PLPDP 是 CASM 最接近的局部周期解码前身。
- PLPDP 已经通过置信度局部调节 DP 的 tempo-consistency penalty。
- dPLP 已经利用多个竞争周期的信息，并在歧义区域抑制过强的周期输出。
- CASM 显式使用 top-versus-competitor margin，并同时调节 duration cost 的强度和容忍度。
- CASM 是面向冻结 activation backbone 的确定性 plug-in，并有独立的 Direct count safeguard。
- beat tracking 中已有 semi-Markov 工作，因此 CASM 的新意不能表述为 semi-Markov 建模本身。

### 不建议写

- “PLPDP 使用固定周期约束。”它使用随时间变化的局部 IBI。
- “PLPDP 在不确定时不会放松约束。”它会通过 confidence 降低 penalty 权重。
- “CASM 是第一个 ambiguity-aware beat decoder。”dPLP 和 masked diffusion 都已经直接处理竞争解释，只是机制和部署设定不同。
- “ambiguity 高时 CASM 自动切换为 Direct。”按照当前方法，低 margin 先使结构代价变弱、变宽；精确 Direct fallback 由事件数异常触发。
- “Real-Time PLP 和 dPLP 是 PLPDP 的直接续作。”它们更准确地说是 PLP 表示的后续分支。

## 我读完后的核心判断

CASM 的最佳叙事不是“比 PLPDP 多一个 confidence”，因为 PLPDP 已有 confidence；也不是“比 dPLP 更懂 ambiguity”，因为 dPLP 已经明确讨论多周期竞争。CASM 更有说服力的组合是：把竞争性 ambiguity 定义为可解释的周期 margin，把它接到稀疏事件级 duration model 上，并在冻结网络、无需学习新参数的条件下，同时处理 beat path、Direct safety 和 beat-synchronous downbeat。这个组合与部署边界才是论文应守住的独特位置。

