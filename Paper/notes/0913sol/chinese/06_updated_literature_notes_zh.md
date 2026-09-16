# CASM Introduction 与 Related Work 文献笔记——中文对照版

**整理模型：** GPT-5.6 Sol  
**日期：** 2026-09-13  
**范围：** 本地 `reading/` 文献、0913 笔记、`casm_v4.tex`，以及相关 calibration / mechanism 审计

## 核心结论

CASM 最合适的定位既不是“第一个 local-period decoder”，也不是“第一个 ambiguity-aware beat tracker”。更严谨且能够保留技术贡献的表述是：

> 一个显式的 best-versus-competitor period margin；该 margin 同时控制稀疏 event-level duration model 的强度和容忍范围，并与独立的 Direct safeguard、downbeat safeguard 结合，用于确定性解码 frozen backbone activations。

这一定位保留了 PLPDP 的关键谱系，承认 dPLP 及 multiple-grid work 已经处理过 ambiguity，同时仍赋予 CASM 清楚的技术与部署身份。

## 八篇本地论文如何启发 Introduction 的开头

| 本地 reading | 开篇方式 | 可供 CASM 使用的部分 |
| --- | --- | --- |
| `01_Beat_This_中文翻译.md`，第 18--30 行 | 先定义 beat tracking，再定义 downbeat tracking，随后介绍 activation-plus-decoder pipeline | P1 与 P2 开头的主要结构模板 |
| `02_BeatFM_中文翻译.md`，第 24--30 行 | 定义时间定位任务后，先说明 downstream uses，再进入技术细节 | 支持 transcription、structure analysis、synchronization 等动机 |
| `03_HingeNet_中文翻译.md`，第 30--44 行 | 把 beat 描述为音乐分析的时间框架 | 支持 “temporal scaffold” 的表达 |
| `04_SMC_Blind_Spot_中文翻译.md`，第 18--26 行 | 简短定义任务，随后进入现代 pipeline 与 failure gap | 适合 P2，但其 benchmark 数字不应放入 P1 |
| `05_Masked_Diffusion_中文翻译.md`，第 28--48 行 | 很快进入 framewise prediction、多种有效 grid 及不连贯 mixture | 更适合 Related Work，不适合作为本文首句 |
| `06_PLPDP_中文翻译.md`，第 19--31 行 | 从 perceived pulse、音乐功能以及 activation-plus-PPT pipeline 切入 | 感知性、功能性开头的主要来源 |
| `07_BeatMamba_中文翻译.md`，第 19--23 行 | 定义任务，并提出局部 transient evidence 与长时间 rhythmic coherence 的张力 | 适合作为进入 decoder 问题的概念桥梁 |
| `08_Chopin_Mazurkas_中文翻译.md`，第 18--24 行 | 对比人类自然打拍与自动系统面对 expressive style 时的脆弱性 | 最有人类直觉的备选开头 |

这些文章形成的共同写法是：**先定义感知任务，再说明输出有何作用，最后进入技术 pipeline 或一般困难。** 具体 F1、CMLt、SMC 数字、模型复杂度和 contribution claim 都应放在更后面。

## DBN：哪些部分是固定的，哪些会适应输入

文献并不支持“DBN 使用一条固定 tempo trajectory”的说法。其 decoded state path 会随 observations 改变，并可以在 tempo、bar-position/phase 和 meter states 之间移动。真正全局配置的是：

- admissible tempo support；
- 联合 beat/downbeat formulation 中的 admissible meter support；
- tempo-transition law 的形式与 stiffness；
- observation/transition weighting 及其他 decoder settings。

PLPDP 的批评对象更具体：常见 HMM/DBN 的 transition likelihood 往往依据经验在全局层面选择，面对 expressive local tempo changes 时可能过强。Beat This! 又把问题扩展到 unsupported meters、out-of-range tempi 和 genre-dependent tempo variability。SMC Blind Spot 则补充了必要的限定：DBN support mismatch 的确可能造成 octave-level errors，但 confidently wrong activations 仍是主要 failure source。因此应当写：

### 有文献支持的英文表述

> DBNs infer an observation-dependent metrical path under globally configured state support and transition preferences; when those assumptions mismatch the music, they can suppress correct local evidence.

中文理解：DBN 推断的节拍路径会响应 observation；风险来自全局配置的 state support 和 transition preferences 与具体音乐不匹配，而不是 DBN 完全不能适应输入。

### 不应使用的表述

- “DBNs do not adapt to the input.”
- “DBNs assume the tempo is constant.”
- “DBNs are the main cause of SMC failure.”

## PLP 谱系与 CASM 的精确边界

| 方法 | 表示或 uncertainty signal | 面对 ambiguity 的行为 | 与 CASM 的关系 |
| --- | --- | --- | --- |
| PLP `\cite{grosche2011plp}` | 在 tempogram 中选取局部主导 periodic kernel，并通过 overlap-add 形成 pulse curve | Hard local period selection 可能把多个竞争解释压缩成单一 winner | 建立 local-pulse representation；本身不是完整 sequence decoder |
| PLPDP `\cite{chiu2023localperiodicity}` | PLP peak spacing 产生分段 local IBI；相邻 PLP peak 的平均高度产生 confidence | 较低 confidence 会降低 DP transition weight | 最接近的 decoder 前身；已经具有 local target 和 confidence-weighted regularization |
| Real-Time PLP `\cite{meier2024realtime}` | 带 stability/lookahead/context outputs 的 causal PLP | 关注在线 controllability 与 zero latency | PLP 的后续分支，而不是对 PLPDP recurrence 的直接修订 |
| dPLP `\cite{chiu2025dplp}` | 对多个 period kernels 进行 softmax weighting | 竞争 kernels 可以发生干涉并减弱 pulse peaks | 说明不能声称 CASM 是第一个 ambiguity-aware method |
| CASM | 最佳局部周期与最强 non-neighbour competitor 之间的 normalized score gap | 低 margin 会减弱并拓宽 duration preference；独立 count test 才可能返回 Direct | 在稀疏 event-level decoder 中显式建模竞争，并区分 soft restraint 与 hard fallback |
| Masked diffusion `\cite{foscarin2026masked}` | 对多种可能 output grids 的 learned distribution | 通过 iterative inference 形成一条 coherent grid | 借助专门 neural training 在上游处理 ambiguity，而不是 frozen-output plug-in |

### PLPDP 最重要的技术细节

在 PLPDP 中，confidence 不只是含糊的 “PLP confidence”。PLP curve 围绕检测到的 peaks 分段；local IBI 来自 peak spacing，每个 segment 的 confidence 则由两侧 boundary peaks 的高度定义（`06_PLPDP_全文中文翻译.md`，约第 86--98 行）。这个 confidence 会调节 DP transition penalty。因此，CASM 不能声称 PLPDP 总是以相同强度执行所选周期。

真正有意义的 gap 更窄：较高的绝对 PLP pulse strength 并不显式意味着所选周期已经明显胜过最强 octave-related 或 neighbouring alternative。CASM 的 runner-up margin 回答的是这一相对关系问题。

## Soft restraint 与 hard fallback 是两套不同机制

当前 CASM algorithm 有两个层次：

1. **局部 soft restraint：** 较小的 period margin 会降低 duration coefficient、扩大 timing tolerance，使 structured path 越来越多地由候选 activation evidence 决定。
2. **全局 hard fallback：** 只有 structured-to-Direct event-count ratio 异常时，才会返回完全相同的 Direct path。

Fig. 1 中竞争周期的例子之所以与 Direct 一致，是因为 duration term 变弱，而不是 ambiguity 直接触发了 router。两个图示案例都没有触发 count safeguard。不要使用 “switches to Direct whenever ambiguity is high”，因为它会暗示不存在的 threshold。

## 应保留的 structured-decoding 历史

Related Work 第一段只需保留能够保护论文定位的历史：

- Ellis DP：经典的 evidence-plus-inter-beat-prior formulation（`ellis2007beattracking`）。
- CRF/probabilistic extraction：其他 structured sequence models（`korzeniowski2014crf`，可选 `fillon2015crf`）。
- Resonating comb filters：显式 dominant-period estimation（`bock2015combfilter`），并非 joint beat/downbeat decoder。
- DBN：标准 neural activation + tempo/phase/meter state-space pipeline（`krebs2015dbn`、`bock2016joint`）。
- Particle filters / BeatNet：causal online hypotheses（`hainsworth2004particle`、`heydari2021beatnet`、`heydari2024beatnetplus`）。
- Heydari 等人的 1D semi-Markov state space：证明 CASM 之前已经存在 semi-Markov rhythm tracking（`heydari2022semimarkov`）。
- Reliability-informed tracking：根据 evidence quality 改变 commitment 的一般思想早于 CASM 的具体 margin（`degara2012reliability`）。

历史段最后应落在一个 design axis，而不是另一个 citation：**temporal prior 从哪里产生？它的有效 constraint law 是全局固定的，还是会根据当前证据改变？**

## Frozen-output setting 之外的替代路线

第三段 Related Work 应把 CASM 与改变系统其他部分的方法区分开：

- Post-processing-free networks 和 Beat This! 把更多时间建模责任放入 predictor training（`chen2022postprocessingfree`、`foscarin2024beat`）。
- Masked diffusion 学习表示并解决多种有效 grids（`foscarin2026masked`）。
- BeatFCOS 与 target-reformulation work 重设 output representation（`ahn2025beatfcos`、`bolt2026reformulated`）。
- User/corpus adaptation 引入 annotations 或 domain-specific tuning（`pinto2021userdriven`、`maia2022adapting`、`maia2024selective`、`pinto2026challenging`）。

这些工作不是同一问题的劣化版本，而是在回答不同的 deployment questions。CASM 的具体 setting 是：已有 tracker 保持冻结，可以取得其 activation outputs，并希望在不重新训练的情况下得到透明、确定性的 sequence decoding。

## 论文 claim 的层级

### 强且有充分支持

- CASM 使用显式 top-versus-competitor local-period margin。
- Margin 同时调节 duration cost 的 strength 与 tolerance。
- Decoder 在 activation-supported candidate events 上搜索。
- Local ambiguity 软化 structured term；count fallback 是独立机制。
- 同一个 globally calibrated configuration 在报告的 tracks、datasets 和 backbones 上保持冻结。
- 推理时不使用逐曲目标注 BPM/meter，也不更新 decoder。

### 需要谨慎限定才可支持

- 较低 calibration burden：只能归因于观察到的 frozen-policy deployment；若要与 DBN 比较 selection sensitivity，必须使用 protocol-matched evidence。
- 更好的 generalization：应说在本文评估的 corpora/backbones 之间迁移，而不是普适 domain generalization。
- Open and ready to use：只有 implementation、license、frozen config、input contract 和 minimal example 均公开后才能使用。

### 应避免

- First local-period beat decoder。
- First ambiguity-aware beat tracker。
- Parameter-free 或 tuning-free。
- Ambiguity 直接使 CASM 切换到 Direct。
- Semi-Markov structure 天然比 DBN 更容易泛化。
- Real-Time PLP 或 dPLP 是 PLPDP 的直接 sequel。

## 建议的章节职责边界

- **Introduction：** 功能性定义；Direct/DBN 张力；一句 PLPDP bridge；CASM mechanism；简短 deployment ending。
- **Related Work：** structured-decoder 历史；详细 PLP/PLPDP/dPLP 谱系；predictor/adaptation alternatives。
- **Methodology：** margin、endpoint aggregation、duration cost、DP 和 exact safeguards 的正式定义。
- **Experiments/Results：** scores、matched support、calibration protocol、sensitivity 与 transfer evidence。

这样既能让 PLPDP 得到足够重视，也不会在 Introduction 和 Related Work 中重复同一套 local-IBI/confidence 解释。
