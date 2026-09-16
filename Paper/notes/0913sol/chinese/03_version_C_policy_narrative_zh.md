# CASM Introduction + Related Work——Version C 中文对照版

**写作模型：** GPT-5.6 Sol  
**定位：** 更鲜明的 policy / generalization 叙事  
**结构：** 严格四段 Introduction、三段 Related Work

本版让一个概念问题贯穿 Introduction：**rhythmic regularity 何时才真正赢得覆盖局部证据的权利？** 这样能够赋予 CASM 更鲜明、容易被记住的身份，同时保持技术 claim 克制。

## 中文对照稿

```latex
\section{引言}
\label{sec:intro}

音乐节拍是一种听者能够跟随或随之打拍的感知脉冲，为组织节奏提供时间框架。Beat tracking 从音频中估计这些脉冲出现的时刻，downbeat tracking 则识别标志小节开始的脉冲。二者共同为音乐转录、结构分析、同步、编辑和交互式音乐应用提供时间参照 \cite{chiu2023localperiodicity,foscarin2024beat}。尽管听者往往可以毫不费力地跟随节拍，自动系统仍需要在弱线索、expressive timing 和多种竞争性的节拍层级解释下保持可靠。

多数现有 tracker 把任务分为 evidence estimation 与 sequence decoding：神经网络产生逐帧 activation，decoder 再将其转换为事件时刻 \cite{bock2016joint}。Direct peak picking 紧密遵循局部 activation，却不会主动保证长时间范围的节奏连贯性。DBN decoding 可以提高连贯性，但也带来互补的风险：它在全局指定的 state support 和 transition preferences 下稳定一条 tempo--phase--meter 路径 \cite{krebs2015dbn,bock2016joint}。该路径仍会响应 observations，但这些 preference 的形式与强度本身并不随局部周期证据的可靠程度改变；不匹配的设置因而可能压制有用的 activation \cite{foscarin2024beat,ahn2026smcblindspot}。PLPDP 则从 predominant local pulse 导出 time-varying inter-beat interval 和 confidence，用它们调节 dynamic-programming penalty 的 target 与 weight \cite{chiu2023localperiodicity}。尚未解决的判断不只是“哪个局部周期最强”，而是“它是否真的比其他解释好到足以被强制执行”。

CASM 把 rhythmic regularity 视为一种必须由输入证据赢得的 commitment。它在 activation 所支持的 peaks 上建立稀疏 semi-Markov path，估计每个 peak 周围的局部周期，并衡量该周期领先最强竞争者的程度。明确的 margin 产生窄而强的 duration preference；较小的 margin 则产生宽而弱的 preference，使路径更多地服从 observation，而不是武断地选择某个节拍层级。Count safeguard 与 beat-synchronous downbeat decoder 分别处理另外两类 path-level failure。Fig.~\ref{fig:casm-examples} 对比了这两种由证据决定的 decoding regimes。

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{figures/p0.jpg}
\caption{CASM 在 SMC 上的 out-of-fold Beat This activation 中作出的示例性决策。当一个周期与其他候选明显分离时，较弱但仍有 activation 支持的事件会被恢复；当多个 period hypotheses 竞争时，duration constraint 会减弱并保留 activation-led 路径。两个例子均未触发独立的 count-ratio safeguard。Reference-derived tempo 只用于解释，从未输入 CASM。}
\label{fig:casm-examples}
\end{figure}

因此，CASM 是一种 decoder policy，而不是 corpus-specific rhythm template：全局 scalars 固定 evidence-to-constraint response law，每条 activation sequence 则决定实际的 period target 与 rigidity。完成一次全局 calibration 后，我们在不同曲目、corpus 和 frozen backbones 上使用同一配置，不重新训练，也不输入逐曲目的 BPM/meter settings；Sec.~\ref{sec:exp} 单独评估了该配置对 calibration data 组成的敏感程度。我们目前提供交互式 demo，并将在论文发表时公开 decoder implementation 和 frozen configuration。

\section{相关工作}
\label{sec:related}

\subsection{节奏结构在何处进入 decoder}
早期 dynamic-programming trackers 把 onset evidence 与主导 inter-beat prior 结合起来 \cite{ellis2007beattracking}。Probabilistic beat extraction、CRF 与 comb-filter methods 提供了不同的事件或周期表示 \cite{korzeniowski2014crf,fillon2015crf,bock2015combfilter}。随后，DBN 建立了最常见的 neural-activation-plus-state-space pipeline，对 tempo、phase 和 meter 进行联合求解 \cite{krebs2015dbn,bock2016joint}。Particle filter 维持因果 tempo hypotheses \cite{hainsworth2004particle}；BeatNet/BeatNet+ 和一维 semi-Markov state space 则把因果推断扩展到联合节奏分析 \cite{heydari2021beatnet,heydari2022semimarkov,heydari2024beatnetplus}。CASM 延续了调和局部证据与序列结构这一共同目标，因此 semi-Markov segment 本身并不是它的 novelty claim。

\subsection{从局部 pulse 到 evidence-dependent commitment}
Predominant local pulse（PLP）通过选择局部显著的 periodic kernels，提取 time-varying pulse \cite{grosche2011plp}。PLPDP 把相邻 PLP peaks 的间隔作为分段局部 inter-beat interval，把这些 peaks 的平均高度作为 confidence；前者提供随时间变化的 target，后者调节 dense-frame dynamic-programming penalty 的权重 \cite{chiu2023localperiodicity}。它因此是 CASM 最接近的方法前身，并且已经建立了 confidence-weighted local decoding。二者的区别在于 confidence 表示什么：PLPDP 衡量所选 pulse curve 中的支持程度，CASM 则显式衡量所选周期相对 next-best period hypothesis 的优势。后续工作把 PLP 扩展到 causal、zero-latency tracking \cite{meier2024realtime}；dPLP 通过 softmax 加权的候选 kernels 使 period selection 可微 \cite{chiu2025dplp}。CASM 不把一般意义上的 period ambiguity 声称为新思想。它把透明的 competitor margin 同时连接到稀疏 event-to-event duration potential 的强度与容忍范围，再以独立、确定性的 safeguards 处理异常事件数量与 downbeat。

\subsection{改变 predictor 或 supervision}
另一些方法把节奏结构放入 predictor，或从附加信息中获得结构。User-driven methods 根据标注适配 tracker \cite{pinto2021userdriven,maia2022adapting,maia2024selective,pinto2026challenging}。包括 Beat This! 在内的 post-processing-free networks 训练 predictor，使其只需要最小 peak picking \cite{chen2022postprocessingfree,foscarin2024beat}；masked diffusion 则学习多个可能节拍网格上的分布，并通过迭代推断选择其中一个连贯结果 \cite{foscarin2026masked}；interval-object 与 target-reformulation methods 进一步重新设计预测问题 \cite{ahn2025beatfcos,bolt2026reformulated}。这些方法与 CASM 是互补的，但通常会改变 predictor、训练方式或 adaptation 时可用的 supervision。CASM 隔离 decoder：它确定性地处理 frozen tracker 的输出，因此可以在不重新训练上游模型的情况下接入。
```

## 何时选择这一版

- 如果希望 reviewer 用一个核心思想记住论文——**regularity 应当由证据决定，而不是被统一强加**——选择 C。
- 最后一段对较低 calibration burden 给出了最清楚的高层解释：全局参数决定 response policy，局部证据决定实际 operating point。
- “在本文中单独评估”把 calibration sensitivity 当作经验问题，而不是关于所有 semi-Markov models 的理论结论。
