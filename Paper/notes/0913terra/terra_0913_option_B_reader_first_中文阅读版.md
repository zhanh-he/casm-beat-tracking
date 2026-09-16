# CASM Introduction + Related Work — Option B：读者优先、较叙事的版本（中文阅读版）

> **terra** 制作，2026-09-13。  
> 对应英文投稿文案：`terra_0913_option_B_reader_first.md`。本文件供中文阅读与比较。

## Introduction：四段的中文对照

节拍跟踪让音乐系统知道演奏在时间中进行到哪里。它找出听者自然跟随的重复脉冲，为转录、结构分析、乐谱--音频对齐以及需要与音乐同步反应的工具提供时间参照。然而，这种脉冲并不总由明显的声音标出：演奏者可能放慢或加快速度，乐器可能轻柔地进入，密集段落也可能暗示不止一个合理的脉冲。听者能够利用前后的音乐语境维持拍感；现有神经节拍跟踪器却可能因为一个看似有说服力的局部线索，而进入错误的速度或拍速 \cite{chiu2023localperiodicity,ru2026beatmamba,ahn2026smcblindspot,foscarin2026masked}。

因此 decoder 必须决定：应当在多大程度上相信局部 activation evidence，又要施加多强的时间规则性。DBN 通过一个关于速度、相位与拍号的全局状态模型来作出这一决定 \cite{krebs2015dbn,bock2016joint}。当它的速度范围、可选拍号和转移行为与音乐一致时，这个模型很有价值；但面对非常规速度、拍号变化或表现性 timing，它们可能变得过于限制 \cite{chiu2023localperiodicity,ahn2026smcblindspot}。PLPDP 让 temporal expectation 更局部：PLP evidence 产生随时间变化的 IBI 与会调节 DP 的 confidence \cite{chiu2023localperiodicity}。这是 activation-derived context 能参与 decoding 的重要先例。不过，选出最强局部周期并不能说明它是否明显优于一个竞争的半速或双速解释。

CASM 让这个差异显式化。它搜索 activation-supported candidate 构成的稀疏图，而不是逐帧搜索。对每个 candidate，它估计局部周期以及最佳周期假设与最接近竞争者之间的 margin。margin 大时，时长偏好更精确且作用更强，因此 CASM 能用清晰周期性跨越一个微弱但有支持的节拍；margin 小时，偏好变宽、变弱，避免一个不可靠的周期覆盖神经证据。count safeguard 与这种局部响应分离：只有结构化路径异常稀疏或稠密时才用 Direct 替换。图~1 对比这两种结果，而不需要额外的 ambiguity router。

最终得到的是一个透明的 plug-in post-processor，服务于已经训练好的 tracker 所给出的兼容 activations。CASM 有一套 validation-selected 全局配置，但其有效约束由每首录音重新计算：这些常数规定面对局部证据时如何响应，而不是为全部输入固定一个 BPM、拍号或 tempo rigidity。这为“当 activation stream 或音乐材料改变时，可能需要更少手动重调”提供了高层理由，同时把这个说法保留为可验证的假设，而非把它当作 semi-Markov 的天然性质。论文会在冻结的 backbones 与数据集上评估该设定，并公开代码、示例和 ready-to-use configuration。

## 图 1：建议 caption 的中文含义

两个来自 SMC 的 held-out 片段，用 Beat This 激活展示 CASM 的 input-conditioned 行为。一个局部周期与替代解释清晰分离时，CASM 可恢复微弱但有激活支持的参考节拍；多个周期假设竞争时，duration term 放松，在本例中 CASM path 与 Direct 重合。DBN 与 PLPDP traces 用于比较；参考标注和参考 IBI 仅用于解释，不是任何 decoder 的输入。

## Related Work：三段的中文对照

后处理问题早于神经 beat activations。早期 DP tracker 形式化了局部起音证据与近似规则 IBI 的权衡 \cite{ellis2007beattracking}。概率化 beat-position extraction \cite{korzeniowski2014crf} 和 resonating comb filter \cite{bock2015combfilter} 以不同方式使周期结构显式化。DBN 随后提供实用的 joint beat/downbeat formulation，将 tempo、phase 与 meter 一起解码 \cite{krebs2015dbn,bock2016joint}。相关的一维 semi-Markov state space 降低了因果联合 rhythm inference 的代价 \cite{heydari2022semimarkov}。CASM 属于这一大类显式 sequence decoder，但它使用稀疏 event graph 和 input-conditioned duration potential，而不是固定 state-space transition law。

PLP 是最直接的概念前身。它从 novelty 或 activation evidence 中提取局部占优、随时间变化的 pulse \cite{grosche2011plp}。在此基础上，PLPDP 把 PLP peaks 转换为局部 IBI trajectory 与 pulse-strength confidence，并把两者注入 framewise DP \cite{chiu2023localperiodicity}。因此 PLPDP 已会在局部证据弱时调整时间约束；不能把 CASM 描写成只是多加一个 “confidence”。区别在于量所测量的对象：CASM 的 margin 对比 selected period 与最强 competitor，并同时改变 event-to-event path 上 duration cost 的 stiffness 和 tolerance。后续 PLP 工作研究因果、可控的估计 \cite{meier2024realtime}，以及竞争周期核的可微 soft mixture \cite{chiu2025dplp}。这些工作既清楚交代谱系，也限定了 CASM 更狭而准确的贡献。

近年的工作还会在 plug-in decoder 之前或之外处理 incoherent activations。在线 particle-filter system 因果地推断 rhythm state \cite{hainsworth2004particle,heydari2021beatnet}；annotation-driven 方法为目标用例适配 tracker \cite{pinto2021userdriven,maia2022adapting}。post-processing-free 网络学习让 predictor 承担更多时间结构 \cite{chen2022postprocessingfree,foscarin2024beat}；masked diffusion 则学习一个迭代机制，从竞争输出中选择连贯 beat grid \cite{foscarin2026masked}。CASM 作出互补的部署选择：不改变 predictor，消费其 frozen activations，再加上确定性的 beat decoding 和 beat-synchronous downbeat decoding。

## 为什么这样写

- 前两句不要求读者先理解 DBN 或 activation decoder；开头最适合广泛 MIR 读者。
- 论文中心张力被明确写成“evidence 与 regularity 应如何权衡”。
- CASM 段将 margin 的渐进放松和 count fallback 分开，避免误写成 ambiguity 直接切换到 Direct。
- 收尾段给出 portability 的解释，但不把目前还无法严格验证的 calibration 结论写成因果事实。
- Related Work 依次承担历史、PLPDP 最近前身、以及其他部署路线三种不同任务。
