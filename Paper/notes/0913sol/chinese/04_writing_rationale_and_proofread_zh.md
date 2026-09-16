# CASM Introduction / Related Work 写作 rationale 与 proofread

**Authoring model:** GPT-5.6 Sol  
**日期:** 2026-09-13  
**审阅对象:** `casm_v4.tex`、0913 三份笔记、`reading/` 中八篇论文，以及 calibration / mechanism audit

## 结论先行

我首推 **Version A**。它最接近你想要的四段 Introduction：第一段先让非专门做 decoder 的读者理解 beat tracking 是什么、有什么用；第二段建立 Direct--DBN--PLPDP 的问题链；第三段只解释 CASM 如何解决这个问题；第四段独立说明它为何更便于迁移和部署，并以公开实现收尾。

如果页数已经非常紧，选 **Version B**。如果你更希望 reviewer 记住一个鲜明的核心命题——“rhythmic commitment must be earned by the input”——选 **Version C**。C 的概念记忆点最强，但语气也比 A 更像 position statement。

## 为什么第一段要彻底换掉

`reading/` 中八篇文章虽风格不同，但主流开篇顺序非常稳定：

| 文章 | 开篇功能 | 借给本稿的东西 |
| --- | --- | --- |
| Beat This! | 直接定义 beat / downbeat tracking | 最清楚的任务定义模板 |
| BeatFM、HingeNet | 定义后说明 transcription、structure analysis 等用途 | “为什么值得做” |
| PLPDP | 从听者会随之敲击的 perceptual pulse 与音乐理解切入 | 最贴近 CASM 论文的功能口径 |
| BeatMamba | 先定义，再讲局部线索与长期连贯性的双尺度难题 | 可作为第二段的概念桥梁 |
| Chopin Mazurkas | 从人类自然打拍与机器跨风格困难的反差切入 | 更有人味的备选开头 |
| SMC Blind Spot | 简短定义后进入 pipeline 与 failure modes | 适合第二段，不适合照搬其数字化开头 |
| Masked Diffusion | 很快进入多解与不连贯预测 | 适合 Related Work，不适合本稿第一句 |

因此三版第一段都遵循：**功能性定义 → 用途 → 现代 pipeline 或普遍挑战**。我没有在第一段放 F1、CMLt、SMC 数字、模型复杂度或某个具体 decoder 的优劣。这不仅更符合阅读材料，也让 Introduction 的入口不依赖读者已经理解 beat-tracking evaluation。

## 四段 Introduction 的职责边界

| 段落 | 只回答什么 | 刻意不做什么 |
| --- | --- | --- |
| P1 | beat/downbeat tracking 是什么；输出为何有用 | 不谈 F1，不谈 CASM，不从 DBN 开始 |
| P2 | activation 变成事件时的 Direct--DBN 张力；PLPDP 带来的 local-prior 转向；尚未解决的 period competition | 不展开 PLP 历史，不写 PLPDP confidence 的计算 |
| P3 | CASM 的 sparse candidates、period competition margin、graded duration preference、两类 safeguard；一句引 Fig. 1 | 不复述图的左右两边，不展开公式 |
| P4 | CASM 的 deployment contract：一次全局 calibration、测试时 input-conditioned、跨输入使用；公开实现 | 不再重复算法步骤，不报具体分数 |

这个分工可以解决 `casm_v4.tex` 的主要结构问题：原 P1 一上来就是 post-processing failure taxonomy；原 P2 已经较完整讲过 PLPDP，Related Work 又讲一遍；原 P3 同时塞了方法、图解、safeguard、calibration、plug-in 与贡献收尾，没有明显落点。

## 三段 Related Work 的思想结构

三段不是简单按年份排文献，而是回答三个不同的 reviewer 问题。

1. **Structured post-processing:** CASM 属于哪一条历史问题？这里从 DP 的 evidence--regularity trade-off，经过 CRF/comb filter，到 DBN 与已有 semi-Markov rhythm tracking。最后落在共同原则：framewise evidence 要作为 sequence 解读。它同时避免把 semi-Markov 本身写成首创。
2. **PLP lineage:** 谁是最近前身，CASM 到底多了什么？这里完整放 PLP → PLPDP → Real-Time PLP / dPLP，并主动承认 PLPDP 已经有 local IBI 与 confidence、dPLP 已经利用竞争周期。CASM 的边界收紧为 explicit top-versus-competitor margin + sparse event-level duration cost 的 strength/tolerance + 独立 safeguards。
3. **Alternative deployment choices:** 结构还可以放在哪里？这里放 particle filter、user adaptation、post-processing-free predictor、masked diffusion、interval/target redesign。段末把 CASM 定位为 frozen-backbone activation decoder，而不是再讲一次 margin。

这样 Related Work 有观点：它不是“别人做了 A、B、C”，而是在比较 **结构放在 decoder、local-pulse representation、predictor 还是交互监督中**。同时，它和 Introduction 分工明确：Introduction 负责问题链，Related Work 负责谱系与 novelty boundary。

## DBN → PLPDP 的事实口径

### DBN 不应被写成“不会适应输入”

DBN 的隐含 tempo / phase / meter path 会随 observation 改变。真正全局固定的是 admissible tempo/meter support、transition-law 的形式，以及 transition stiffness 等配置。因此我统一使用：

> the inferred trajectory depends on the observations, but its state support and transition law are specified globally

这比 “DBN uses a fixed tempo” 准确，也与 PLPDP 原文的批评对象一致。PLPDP 反对的是 **globally parameterized, empirically chosen transition likelihoods 在 expressive timing 上可能过强**，不是声称 HMM/DBN 只能输出恒速路径。

SMC Blind Spot 还要求再加一层克制：SMC 的主要错误往往仍来自 confidently wrong activations；DBN support mismatch 是重要 failure mode，但不是所有 beat-tracking failure 的根因。因此正文应写 “mismatched priors can override useful local evidence”，不应写 “DBNs are the main cause of failure”。

### PLPDP 已经做到了什么

PLPDP 已经：

- 从 activation-derived PLP 获得 time-varying local IBI；
- 用相邻 PLP peak heights 形成 confidence；
- 用 local IBI 改变 DP 的 target，用 confidence 调节 penalty weight；
- 在 confidence 较低时减弱结构约束。

所以不能写 “PLPDP applies the same constraint regardless of uncertainty”。CASM 更精确的差异是：PLPDP 的 confidence 来自所选 pulse 的显著性，并不显式度量最佳 period 相对 strongest competitor 赢了多少；CASM 的 margin 正在回答后一个问题。

### dPLP 决定了 novelty claim 的上限

dPLP 用 softmax 混合多个周期核，竞争核能够通过相位干涉削弱最终 pulse。因此 “CASM is the first ambiguity-aware beat decoder” 太大。三版均把贡献限定为：**explicit competitor margin 如何进入 sparse event-to-event duration potential，以及它如何同时控制 strength 与 tolerance**。

Real-Time PLP 也不应再称为 “PLPDP's real-time continuation”。它延伸的是 PLP 表示与实时交互方向，不是 PLPDP 动态规划递推式的直接续作。

## Fig. 1 proofread

原稿正文和 caption 连续两次复述 “on the left / on the right”，而图面标题本身已经再次说了同一件事。三版改为：

- 正文只说 Fig. 1 的功能：它把 graded policy 变成可见案例；
- caption 承担两个具体 operating regimes；
- 不再使用 left/right；
- 明确两例都没有触发 count safeguard；
- 把右例称为 “activation-led path remains unchanged”，而不是让人误解为 ambiguity threshold 触发了硬切换到 Direct。

另一个细节是：图的纵轴单位是 BPM，黑线实际是由 reference IBI 换算出的 tempo。建议把图中 legend 的 **Reference IBI** 也改为 **Reference-derived tempo**；三版 caption 已按这个准确名称写。reference 只供解释，从未输入 decoder。

图内右侧标题目前仍写着 **CASM defers**，容易让人以为 ambiguity 触发了硬 fallback。建议改为 **Competing periods: observation-led output**。这两个图内文字修改需要重新导出 `p0.jpg`；本次交付只改写文稿，没有改动原图或源代码。

## 为什么 CASM 可能更少依赖 calibration：正确的高层解释

最清楚的说法不是 “CASM has fewer parameters”，也不是 “semi-Markov naturally generalizes”。真正差别在参数所规定的对象：

- 全局 CASM scalars 规定一条 **evidence-to-constraint response law**；
- 每首新曲目的 activation 决定 local period target、period separation，以及实际 duration stiffness；
- 因而 calibration 选择的是“看到某种局部证据时该怎样响应”，不是为每个 corpus 或 track 固定一套 tempo trajectory / meter template；
- adaptive 部分使用 activation 内部的关系量——候选事件间距与 competing-period separation——所以相同 policy 可以在不同 backbone 和 corpus 上落到不同 operating points。

这是一条合理的机制解释，也与现有 Fig. 1 mechanism audit 对得上；但它不是普适泛化定理。建议按证据强度分三档写：

| 证据状态 | 可用表述 |
| --- | --- |
| 当前最安全 | “A single globally calibrated configuration is frozen and applied across tracks, corpora, and backbones without per-track BPM/meter tuning.” |
| 完成公平 matched calibration 后 | “Under the prespecified matched-support protocol, CASM selection is less sensitive than DBN selection to which labelled calibration folds are available.” |
| 不建议 | “CASM is parameter-free”; “semi-Markov is intrinsically more robust”; “CASM guarantees domain generalization.” |

### 当前必须核对的 calibration provenance

`casm_v4.tex` 现在写成 CASM 与 DBN 都在相同 SMC fold subsets 上独立选配置；但 2026-09-05 的审计记录显示，当时实际流程并不 matched：CASM 的 fold inventory 包含多 corpus、每个 1F 约 562--575 tracks，而 DBN 只用 SMC、约 27--28 tracks；selection objective 与 search procedure 也不同。

在找到审计之后的公平重跑记录以前，下面两处不宜作为定稿强结论：

- Abstract 的 “CASM is less sensitive than DBNs to the choice of calibration data”；
- Results 的 “consistent with stronger calibration-set over-specialisation in the fixed DBN parameterisation”。

如果公平重跑已经在别处完成，请把 exact inventory、selection utility、support restriction 和 result file 补进 provenance；届时 Version C 的 closing 最合适。若尚未完成，Version A 的 policy-level transfer 说法最稳。

## “开源、调好、立刻可用”怎样写才经得住检查

论文可以写 “We release the implementation and a ready-to-use configuration”，但投稿时公开仓库最好同时具备：

- 实际 CASM decoder implementation，而不只是静态 listening demo / figure reproduction code；
- 明确 license；
- 冻结的默认配置及其版本或 checksum；
- 一条最小运行示例：输入 activation 的 shape / frame rate / logit-or-probability contract，输出 beat/downbeat times；
- 依赖与安装说明；
- 论文结果所用 configuration 与代码默认值一致。

当前本地仓库首页明确公开了 demo，但从顶层 README 尚不能直接确认上述完整 drop-in contract。因此三版里的 release 句应视为 **camera-ready 时必须兑现的声明**。若提交前还没补齐，暂时改成：

> We provide an interactive demo and will release the decoder implementation and frozen configuration upon publication.

补齐实现、license、冻结配置和最小示例之后，可以把收尾升级为：

> We release CASM as a drop-in decoder, together with the frozen configuration used in all experiments, installation instructions, and a minimal activation-to-events example.

另外，`casm_v4` 的 Abstract 已经给项目 URL 加了 footnote，所以三版默认稿不在 Introduction 重复该脚注。若之后把链接移到 Introduction，请同步删除 Abstract 中的版本；同一个短链接不应在相邻首页内容中出现两次。

当前公开地址仍含 `icassp2026`，而投稿目标是 ICASSP 2027。重定向本身不影响技术内容，但 camera-ready 前最好提供一个稳定、年份一致的入口。

## 三版选择表

| 版本 | 约略字数（Intro / RW，含图注与 LaTeX 标记） | 主要优点 | 主要代价 | 建议用途 |
| --- | ---: | --- | --- | --- |
| A — Balanced | 452 / 398 | 最均衡；事实边界和叙事都完整；Related Work 最扎实 | 字数最长 | 默认主稿 |
| B — Compact | 377 / 279 | 最省版面；仍保留 PLPDP/dPLP 核心边界 | 次要历史和 calibration 论证较薄 | 接近页限时 |
| C — Policy narrative | 462 / 368 | 记忆点最强；“decoder policy vs corpus template”最好地解释迁移 | 语气较鲜明；更依赖 calibration provenance 完整 | 机制与部署是主卖点时 |

按当前 `casm_v4` 的双栏版式进行整稿试编译时，A 与 C 均为 6 页，且 Introduction 的最后一段跨到第 2 页；B 为 5 页，Introduction 在第 1 页收完、Methodology 从第 2 页开始。因此 B 是当前最安全的页数方案。若采用 A/C，优先把 P4 压到约 35--45 词，或把 Fig. 1 环境移到 P4 之后再重新编译，而不是删掉 PLPDP/dPLP 的 novelty-boundary 段。

## 我建议最终如何拼

如果直接整版采用，我仍建议 Version A，因为它的风险最低、改动最容易与现稿其余章节同步。若允许混搭，文字上最有记忆点的组合是：

- Version C 的四段 Introduction；
- calibration provenance 尚未核实完时，把 C 的 P4 换成 Version A 的 P4；
- Version A 的三段 Related Work；
- Version B 的长度只作为压缩目标，而不是先删 PLPDP / dPLP 段。

压字时的删除顺序应是：第三段 Related Work 中 BeatFCOS / target reformulation → 第一段中的 CRF 细支 → online/user-adaptation 旁支。最后才动 PLP lineage；那一段是 reviewer 判断 novelty 的核心。
