# CASM Introduction + Related Work——Version B 中文对照版

**写作模型：** GPT-5.6 Sol  
**定位：** 紧凑 ICASSP 版本  
**结构：** 严格四段 Introduction、三段 Related Work

本版面向严格的页数预算。它保留 PLPDP 与 dPLP 所限定的 novelty boundary，但从论文正文中删去了大部分次要历史和较长的部署限定语。

## 中文对照稿

```latex
\section{引言}
\label{sec:intro}

Beat tracking 定位听者可能随之打拍的感知脉冲，downbeat tracking 则识别其中标志小节开始的脉冲。由此得到的时间线可服务于音乐转录、结构分析、同步和交互式应用 \cite{chiu2023localperiodicity,foscarin2024beat}。现代系统通常先估计逐帧 beat/downbeat activation，再把它们解码为离散事件 \cite{bock2016joint}。Decoder 需要在保留可信 activation evidence 的同时，使输出节奏在时间上保持连贯。

Direct peak picking 紧贴 activation，但可能留下漏检、重复或节拍层级不一致的事件。DBN 通过在预先定义的状态支持范围和 transition law 下推断 tempo、phase 与 meter 来提高连贯性 \cite{krebs2015dbn,bock2016joint}。当这些设置与输入音乐相符时，它们十分有效；但面对特殊 meter、极慢 tempo 或 expressive timing，也可能覆盖正确的局部证据 \cite{foscarin2024beat,ahn2026smcblindspot}。PLPDP 则从 predominant local pulse 导出 time-varying inter-beat interval 与 confidence，并用二者调节 dynamic-programming penalty 的 target 和 weight \cite{chiu2023localperiodicity}；尚未解决的是，当另一种节拍层级解释几乎同样合理时，应当在多大程度上相信这一估计。

CASM 在 activation 所支持的 peaks 上建立稀疏 semi-Markov path 来回答这个问题。它估计领先的局部周期及其相对最强竞争周期的分离度，再利用该 margin 同时控制 segment-duration preference 的强度与容忍范围。因此，在 ambiguous regions 中，解码会更多地遵循 activation，而不是被迫落入一条不确定的节拍网格。独立的 beat-count safeguard 会在结构化结果过密或过疏时返回 Direct 路径，downbeat 则在已经选定的 beat grid 上解码。Fig.~\ref{fig:casm-examples} 展示了这两种互补的工作状态。

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{figures/p0.jpg}
\caption{CASM 在 SMC 上的 out-of-fold Beat This activation 中作出的示例性决策。当某个周期明显胜出时，CASM 能够恢复较弱但仍有 activation 支持的事件；当多个周期相互竞争时，duration preference 会减弱，并保留 activation-led 路径。两个例子均未触发独立的 count-ratio safeguard，reference-derived tempo 只用于辅助解释。}
\label{fig:casm-examples}
\end{figure}

CASM 只 calibration 一次，但它的固定参数定义的是每条输入应当如何控制 decoder，而不是向所有曲目施加同一个 tempo target 或 transition rigidity。在本文报告的实验中，我们在不同曲目和 backbone 上使用一个 frozen configuration，不重新训练，也不进行逐曲目的 BPM/meter 调整。我们目前提供交互式 demo，并将在论文发表时公开 decoder implementation 与 configuration。

\section{相关工作}
\label{sec:related}

Dynamic programming 确立了在 onset evidence 与 inter-beat regularity 之间进行平衡的经典形式 \cite{ellis2007beattracking}。Probabilistic beat extraction 与 resonating comb filter 分别带来了基于事件和周期性的替代表述 \cite{korzeniowski2014crf,bock2015combfilter}；DBN 则通过在状态空间轨迹中联合建模 tempo、phase 和 meter，成为最主要的 beat/downbeat decoder \cite{krebs2015dbn,bock2016joint}。因果一维 state space 中的 semi-Markov rhythm tracking 也已有探索 \cite{heydari2022semimarkov}。这些方法共同说明，structured sequence inference 长期以来一直是 framewise activation 的重要补充。

PLP 从局部主导周期生成 time-varying pulse representation \cite{grosche2011plp}。PLPDP 是与 CASM 最接近的方法先例：它把相邻 PLP peaks 的间隔作为分段局部 inter-beat interval，把两个 peaks 的平均高度作为 confidence；前者提供随时间变化的 target，后者调节 dense-frame dynamic-programming penalty 的权重 \cite{chiu2023localperiodicity}。因此，PLPDP 在低 confidence 下已经会减弱结构约束，但不会显式比较所选周期与其最强竞争周期。后续工作把 PLP 扩展到 causal、zero-latency tracking \cite{meier2024realtime}，dPLP 则通过对候选 kernels 进行 softmax 加权，使 period selection 可微 \cite{chiu2025dplp}。CASM 更窄也更准确的贡献是：用显式 period-separation margin 控制稀疏 event-level duration cost 的强度与宽度，并配合独立的 beat-count safeguard 和 beat-synchronous downbeat decoder。

其他路线改变的是部署条件、predictor 或可用 supervision。Online particle-filter systems 在因果推断过程中维持 tempo hypotheses，user-adaptive trackers 则从标注中学习 \cite{heydari2021beatnet,heydari2024beatnetplus,pinto2021userdriven}。Post-processing-free networks 与 Beat This! 针对最小化 peak picking 的需求进行训练 \cite{chen2022postprocessingfree,foscarin2024beat}，masked diffusion 则通过迭代 neural inference 对多个可能的节拍网格建模 \cite{foscarin2026masked}。CASM 保留了针对既有模型的确定性 post-processing 角色，只需要其 activation outputs，不要求额外训练 backbone。
```

## 何时选择这一版

- 当全文已经接近 ICASSP 页数上限时选择 B。
- 它保留 reviewer 最需要看到的引用，但删去了 BeatFCOS、target reformulation、更完整的 CRF 历史及较长的 calibration 论述。
- dPLP 仍被保留，因为它对限定 novelty claim 的价值高于上述旁支。
