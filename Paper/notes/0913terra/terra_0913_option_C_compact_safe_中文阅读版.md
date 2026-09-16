# CASM Introduction + Related Work — Option C：紧凑、证据边界最稳妥的版本（中文阅读版）

> **terra** 制作，2026-09-13。  
> 对应英文投稿文案：`terra_0913_option_C_compact_safe.md`。本文件供中文阅读与比较。

## Introduction：四段的中文对照

音乐常让我们在下一个事件到来之前，就自然地打拍、摆动或有所期待。自动节拍跟踪试图从音频中恢复支撑这种体验的脉冲，从而为转录、结构分析和能随音乐作出反应的应用提供时间参照。只有当脉冲清楚且规则时，这个任务才相对直接。对于表现性或不寻常的段落，速度变化、微弱的起音、密集的织体，或几种都说得通的听拍方式，都可能让系统找不到唯一明确的答案；神经模型于是可能每一刻的预测都看似合理，却无法拼成一个稳定的节奏解释 \cite{chiu2023localperiodicity,ru2026beatmamba,foscarin2026masked}。

一种常见解法是 DBN：它在全局指定的 state support 与 transition assumption 下，解码联合的 tempo、phase、meter trajectory \cite{krebs2015dbn,bock2016joint}。这些结构假设与录音相符时可以修正局部错误，但当 tempo、meter 或 timing behavior 超出这些假设时，也会拒绝 activation-supported event \cite{foscarin2024beat,ahn2026smcblindspot}。PLPDP 提供重要的局部替代方案：它从 PLP evidence 导出 time-varying IBI 和 confidence signal，用 locally conditioned DP 取代单一 global target \cite{chiu2023localperiodicity}。但 pulse strength 不能直接说明某一个周期是否确实优于竞争的 half- 或 double-tempo explanation。

我们提出 CASM：一个面向兼容 frozen activation model 的 context-aware semi-Markov post-processor。CASM 在 activation-supported peak 上搜索稀疏路径，同时估计局部周期及其与最强竞争周期的分离度。这些量决定 event-to-event duration preference 的中心与尺度：局部证据清晰时可以做坚定的节奏修正；证据模糊时路径会逐步变得更 activation-led。这是分级的 relaxation，而非 ambiguity 触发的 Direct peak-picking switch；另一个独立的 beat-count safeguard 会在结构化输出异常稀疏或稠密时返回 Direct。图~1 呈现这两种 operating regime，随后 beat-synchronous meter decoder 在选定 beat grid 上生成 downbeat。

CASM 的目标是让 structured decoding 更可迁移，而不是宣称没有参数。它的 validation-selected global constants 定义一条 evidence-to-constraint response law；每首录音的 local activations 则在推断时决定实际的 target period、tolerance 和 stiffness。因此，同一份 frozen configuration 在所评估设定中无需 backbone retraining、逐曲 BPM 或 meter setting。论文在三个 frozen backbone 和两个数据集上检验这种 transfer，并公开实现和校准后的 configuration 供直接使用。

## 图 1：建议 caption 的中文含义

两个 SMC held-out 片段展示 CASM 的 input-conditioned behavior。局部周期与替代解释充分分离时，它可支持恢复微弱但有 activation 支持的参考节拍；周期假设竞争时，duration term 放松，CASM path 在本例中与 Direct 重合。DBN 和 PLPDP traces 用于对比。参考标注和参考 IBI 仅用于解释，不是 decoder 输入。

## Related Work：三段的中文对照

结构化后处理把逐帧 beat evidence 转成连贯 event sequence。DP 在事件证据与 tempo-derived interval preference 之间权衡 \cite{ellis2007beattracking}；probabilistic beat-position model 和 CRF 提供不同的 sequence formulation \cite{korzeniowski2014crf,fillon2015crf}；resonating comb filter 估计周期性以辅助 tracking \cite{bock2015combfilter}。DBN 仍是重要的 joint decoder，因为它把 tempo、phase、meter 放入同一条路径 \cite{krebs2015dbn,bock2016joint}。Semi-Markov state-space model 也已用于高效 causal rhythm tracking \cite{heydari2022semimarkov}。这些方法确立了 activation network 之后继续做 structured decoding 的价值，但通常依赖 globally specified timing behavior。

最接近的工作线是 local-periodicity decoding。PLP 表示随时间变化的 pulse evidence \cite{grosche2011plp}；PLPDP 把 PLP peak 转为 local IBI 和 pulse-strength confidence，以条件化 DP \cite{chiu2023localperiodicity}。后续 PLP 工作研究 causal/controllable operation \cite{meier2024realtime}，以及可微 pulse estimation；后者中竞争周期可削弱最终的 pulse representation \cite{chiu2025dplp}。因此 CASM 不应声称 local periodicity 或 ambiguity handling 本身新颖。其具体区别是使用显式 dominant-versus-competitor margin，为 frozen tracker activations 的稀疏 event-level duration model 提供条件。

其他方法把 coherence 问题移到专门训练的 predictor 或不同 deployment setting 中。post-processing-free tracker 追求可直接 peak-pick 的输出 \cite{chen2022postprocessingfree,foscarin2024beat}；masked diffusion 用经过修改和重训的 predictor 迭代构造连贯序列 \cite{foscarin2026masked}。particle-filter tracker 面向 online inference，user-driven 方法用额外 annotation 适配 tracker \cite{hainsworth2004particle,heydari2021beatnet,pinto2021userdriven,maia2024selective}。CASM 则保留 frozen backbone，提供确定性 plug-in decoder，且只在 activation evidence 支持时使用 local structure。

## 为什么这样写

- 这是三版中术语最严格的一版：使用 validation-selected、frozen、compatible activation models，而不写 parameter-free、tuning-free 或无边界的 model-agnostic。
- 它给出可审计的高层机制：低维的全局 response policy 在每条 edge 上产生 input-derived local constraint；不会宣称 CASM 天生具备优越的 calibration 性质。
- 它准确说明 DBN 的 state support/transition assumption 是全局指定的，而不是错误地说 DBN 不会根据观测适应 tempo/phase path。
- 这是篇幅最紧凑、同时保留 PLP--PLPDP--dPLP 谱系与三段式 Related Work 的候选。
