# CASM Introduction + Related Work — Option A：平衡、面向审稿人的版本（中文阅读版）

> **terra** 制作，2026-09-13。  
> 对应英文投稿文案：`terra_0913_option_A_balanced.md`。本文件供阅读与比较；英文文件才是可直接粘贴进论文的版本。

## Introduction：四段的中文对照

节拍跟踪要从一段音频录音中估计音乐节拍何时出现——也就是听者可能会自然随之敲击的感知脉冲。这个脉冲帮助人们跟随演奏，也为音乐转录和结构分析等任务提供时间参照 \cite{chiu2023localperiodicity,ru2026beatmamba}。节拍清晰、速度稳定的音乐可能很容易跟随；但遇到表现性速度处理、微弱或模糊的起音、密集的复调织体，或不止一种合理的节拍层级解释时，自动系统仍很难确定节拍 \cite{chiu2023localperiodicity,ru2026beatmamba,foscarin2026masked}。这些情形说明，即使标准基准上的表现不断改善，节拍跟踪仍是一个开放问题 \cite{ahn2026smcblindspot}。

大多数当代系统先把音频转成逐帧节拍激活，再把这些激活解码成事件序列。在常见的 DBN 表述中，推断会在离散化的速度--相位--拍号状态空间中寻找一条轨迹；速度支持范围、转移行为和允许的拍号均为全局设定 \cite{krebs2015dbn,bock2016joint}。当这些约束与录音相符时，它们能提升连贯性；但在表现性速度、未被支持的速度范围或拍号下，它们也可能与有激活支持的事件发生冲突 \cite{foscarin2024beat,ahn2026smcblindspot}。PLPDP 提供了一条重要的局部替代路径：它从主导局部脉冲（predominant local pulses, PLP）中导出随时间变化的估计节拍间隔和周期性置信度，并以这些局部量替换 DP 中固定的目标与权重 \cite{chiu2023localperiodicity}。这说明 timing constraint 可以由局部证据来条件化；但 pulse strength 本身并不直接度量领先周期是否确实与最强竞争者拉开了足够差距。

我们为此提出 Context-Aware Semi-Markov（CASM）解码。CASM 在由激活支持的峰值上构造稀疏路径，并在每个候选点估计局部周期，以及领先周期假设与其最强竞争假设之间的分离度。这个 margin 同时控制候选点间时长代价的强度和容忍度：周期证据明确时，CASM 可以坚定地利用局部规则性；竞争假设接近时，它会放松约束，让激活证据更主导路径。另有一个独立的事件数 safeguard：只有结构化结果异常稀疏或异常密集时，才返回 Direct 路径。图~1 展示了这两种预期行为：周期明确时，CASM 可恢复微弱但有激活支持的节拍；周期竞争时，其输出在该例中与 Direct 一致。

CASM 是一个面向兼容、冻结激活流的确定性 plug-in：不需要重训 backbone，也不需要逐曲提供 BPM 或拍号设置。一套全局 decoder configuration 在 development data 上选择后即被冻结；但测试时，其实际生效的时长约束仍会响应每首录音的局部证据。从更高层看，这些固定常数定义的是可复用的“响应规则”——应多大程度信任从输入得到的局部周期——而不是为某个语料库指定一种固定的速度刚性。该 input-conditioned 设计意在让配置能够跨录音、backbone 与数据集迁移；论文评估这一 deployment contract，并公开可直接使用的实现和配置。

## 图 1：建议 caption 的中文含义

两个来自 SMC 的 held-out 片段，用 Beat This 激活展示 CASM 的 input-conditioned 行为。一个局部周期与替代假设充分分离时，CASM 可以借助它恢复微弱但有激活支持的参考节拍；多个周期假设竞争时，时长项会放松，在本例中 CASM 路径与 Direct 重合。DBN 和 PLPDP 轨迹仅用于比较。参考标注和参考 IBI 仅用于解释，任何 decoder 都不使用它们作为输入。

这里刻意不再复述“左/右”：图的面板布局和标题已经承担了该功能。

## Related Work：三段的中文对照

结构化后处理长期以来都在把逐帧节拍证据转成事件序列。动态规划在起音证据和预设的节拍间隔规则性之间进行权衡 \cite{ellis2007beattracking}；概率化的 beat-position 模型提供另一种事件提取表述 \cite{korzeniowski2014crf}；resonating comb filter 则先估计周期性再参与对齐 \cite{bock2015combfilter}。DBN 联合建模速度、相位和拍号，以解码全局一致的 beat/downbeat 路径 \cite{krebs2015dbn,bock2016joint}。Semi-Markov state space 也已被用于高效的因果联合节奏推断 \cite{heydari2022semimarkov}。这些方法在状态表示和推断方式上不同，但都把显式的时间模型放在 activation predictor 之外。

与 CASM 最接近的谱系是 local-periodicity decoding。PLP 从局部具有周期性的起音或激活证据中估计随时间变化的脉冲 \cite{grosche2011plp}。PLPDP 分别把 PLP 峰的间隔与高度转成局部 IBI 目标和 pulse-strength confidence，并将两者用于 dense-frame DP \cite{chiu2023localperiodicity}。因此，PLPDP 在 PLP 证据较弱时已经会减弱节奏惩罚；但它的 confidence 并不显式量化领先周期和竞争周期之间的差距。后续 PLP 工作将 pulse estimation 做成因果且可控 \cite{meier2024realtime}；dPLP 则把硬性的周期选择替换为候选核的可微混合 \cite{chiu2025dplp}。因此 CASM 不应声称“首次处理 ambiguity”。它的区别在于，用 top-versus-runner-up period margin 同时调节稀疏 candidate-to-candidate duration cost 的强度和容忍度，并且有独立的 event-count safeguard 可返回 Direct。

还有一些工作通过不同的部署选择来降低对传统 decoder 的依赖。Particle-filter 系统进行在线 rhythm-state inference \cite{hainsworth2004particle,heydari2021beatnet,heydari2024beatnetplus}；面向目标的 adaptation 会利用额外标注重调 tracker \cite{pinto2021userdriven,maia2022adapting}。post-processing-free 网络则把更多时间建模移入 predictor training \cite{chen2022postprocessingfree,foscarin2024beat}；masked diffusion 以学习式迭代推断明确建模竞争的 beat grid \cite{foscarin2026masked}。CASM 针对的是另一个场景：frozen tracker 已经给出 activations，CASM 作为确定性的 plug-in decoder 使用这些输出，并在选择出的 beat grid 上解码 downbeat，无需重训 backbone。

## 为什么这样写

- 第一段从 beat tracking 的功能性定义开始，而不是从 DBN 争论或某个 metric 开始。
- 第二段准确复述 PLPDP 对全局 tempo assumption 的修正，不暗示 DBN 从不适应输入，也不抹去 PLPDP 已有的 confidence。
- 第三段只解释一次 CASM 机制；图的句子只说明两种行为，不重复面板布局。
- 第四段给出 portability 的部署层解释：全局参数定义的是 input-conditioned response rule。它刻意不宣称 CASM 天生比 DBN 更不受 calibration 影响，因为目前的 calibration comparison 尚未完全协议匹配。
- Related Work 的职责与 Introduction 分离：先历史定位，再精确说明 PLP--PLPDP--dPLP 谱系，最后说明不同的 deployment route。
