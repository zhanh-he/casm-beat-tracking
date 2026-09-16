# CASM Introduction + Related Work——Version A 中文对照版

**写作模型：** GPT-5.6 Sol  
**定位：** 均衡、推荐  
**结构：** 严格四段 Introduction、三段 Related Work  
**资料基础：** `casm_v4.tex`、三份 0913 笔记、本地 `reading/` 文献集，以及 calibration / mechanism 审计

本版保留 `casm_v4` 中最有价值的内容，但把 Introduction 的入口改成读者友好的功能性介绍。PLP 的完整谱系留在 Related Work，Introduction 最后一段则独立总结部署与迁移意义。

## 中文对照稿

```latex
\section{引言}
\label{sec:intro}

Beat tracking 估计听者会自然随之打拍的感知脉冲在时间上的位置；downbeat tracking 则进一步识别每个小节的起始位置 \cite{chiu2023localperiodicity,foscarin2024beat}。这些事件共同构成理解和组织音乐节奏的时间骨架，并服务于音乐转录、结构分析、同步和交互式音乐系统等应用。尽管听者往往能够毫不费力地感知节拍，但当声学线索较弱、速度发生表现性变化，或存在多种可能的节拍层级解释时，自动跟踪仍然十分困难。

多数现代系统首先把音频映射为逐帧的 beat 和 downbeat activation，再把这些曲线解码为离散事件 \cite{bock2016joint}。最简单的 decoder 直接选择 activation 的局部极大值，能够保留网络的局部判断，却难以防止重复、漏检或节拍层级不一致的事件 \cite{foscarin2024beat}。Dynamic Bayesian network（DBN）则通过推断联合的 tempo--phase--meter 轨迹来施加时间连贯性，至今仍是最常用的结构化解码方式 \cite{krebs2015dbn,bock2016joint}。其推断轨迹会随 observation 改变，但 tempo 支持范围、允许的 meter 以及 transition law 都在看到具体曲目之前全局设定；当这些假设与极慢、表现性时值显著或结构特殊的音乐不匹配时，prior 可能压制本来有用的局部证据 \cite{foscarin2024beat,ahn2026smcblindspot}。PLPDP 表明，decoder 的 timing constraint 可以改由局部周期证据产生 \cite{chiu2023localperiodicity}。这进一步引出一个问题：当多种节拍层级解释都具有合理性时，当前证据究竟赢得了多大程度的 rhythmic commitment？

我们提出 CASM：一个在 activation 所支持的候选事件稀疏图上进行搜索的 context-aware semi-Markov decoder。对于每个候选事件，CASM 比较占主导的局部周期与最强备选周期，并利用这种竞争关系连续调节事件之间的节奏约束。当二者的分离度减小时，duration preference 会相应减弱，解码路径也会越来越多地服从 activation。一个独立的 beat-count safeguard 会在结构化结果过密或过疏时返回 Direct 路径，而 beat-synchronous meter decoder 则保证 beat 与 downbeat 的一致性。Fig.~\ref{fig:casm-examples} 用 held-out activation 具体展示了这些行为。

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{figures/p0.jpg}
\caption{CASM 在 SMC 上的 out-of-fold Beat This activation 中作出的示例性决策。当某个周期与其他候选明显分离时，CASM 能够恢复较弱但仍有 activation 支持的事件；当多个周期相互竞争时，duration preference 会减弱，并保留 activation-led 路径。两个例子均未触发独立的 count-ratio safeguard；reference-derived tempo 仅用于解释，从未输入 decoder。}
\label{fig:casm-examples}
\end{figure}

CASM 用一次全局 calibration 后固定的 decoder policy 取代逐曲目的 timing assumptions：全局常量规定局部证据应当如何控制 decoder，而不是为每个输入预先规定同一种节奏状态。由于每条 activation sequence 都会决定自己的局部 target 和 constraint strength，我们在不同曲目、corpus 和 backbone 上使用同一配置，推理时不做逐曲目 calibration。我们目前提供交互式 demo，并将在论文发表时公开 decoder implementation 和 frozen configuration。

\section{相关工作}
\label{sec:related}

\subsection{结构化后处理}
Beat-tracking post-processor 长期以来一直把事件提取视为 sequence inference。Dynamic programming 在 onset evidence 与 inter-beat regularity prior 之间进行平衡 \cite{ellis2007beattracking}；Bayesian 和 CRF-based extractor 从 activation function 中推断 beat position \cite{korzeniowski2014crf,fillon2015crf}；resonating comb-filter bank 则显式估计主导周期 \cite{bock2015combfilter}。DBN 通过在 tempo、phase 和 meter 构成的状态空间中寻找时间连贯的轨迹，成为标准的联合 decoder \cite{krebs2015dbn,bock2016joint}。Particle filter 维持因果的 tempo hypotheses \cite{hainsworth2004particle}；BeatNet/BeatNet+ 以及紧凑的一维 semi-Markov state space 将因果推断扩展到联合节奏分析 \cite{heydari2021beatnet,heydari2022semimarkov,heydari2024beatnetplus}。这些方法的表示与推断过程虽然不同，却都遵循同一原则：有噪声的逐帧证据应当作为一个序列来解释，而不是逐帧独立地进行阈值判断。

\subsection{局部周期与竞争解释}
Reliability-informed tracking 较早确立了“时间约束的投入程度可以随证据质量改变”这一更一般的思想 \cite{degara2012reliability}。与 CASM 最接近的方法谱系从 predominant local pulse（PLP）开始：PLP 从局部主导周期构造随时间变化的 pulse representation \cite{grosche2011plp}。PLPDP 把相邻 PLP peaks 之间的间隔作为分段局部 inter-beat interval，并以这两个 peaks 的平均高度作为 confidence；前者提供随时间变化的 target，后者调节 dense-frame dynamic-programming penalty 的权重 \cite{chiu2023localperiodicity}。因此，PLPDP 在 confidence 较低时已经会减弱时间结构。其 confidence 反映的是所选 pulse 的显著性，却不直接表示该周期相对最强竞争解释领先了多少。后续工作把 PLP 扩展到 causal、zero-latency tracking \cite{meier2024realtime}；dPLP 则以 softmax 加权的多个 periodic kernels 取代 hard period selection，使竞争 hypotheses 可以共同影响 pulse representation \cite{chiu2025dplp}。因此，CASM 并不把一般意义上的 ambiguity handling 声称为首创。它的区别在于：以显式的 top-versus-competitor period margin 同时控制稀疏 event-to-event duration cost 的强度与容忍范围；此外，独立的 event-count safeguard 可以返回 Direct 路径，downbeat 则由 beat-synchronous decoder 处理。

\subsection{改变 predictor 或 supervision}
另一些工作通过改变 predictor 的学习内容或引入 adaptation data，减少对传统固定 decoder 的依赖。User-driven systems 利用标注调整 tracker \cite{pinto2021userdriven,maia2022adapting,maia2024selective,pinto2026challenging}。包括 Beat This! 在内的 post-processing-free networks 把更多时间建模责任放入 predictor \cite{chen2022postprocessingfree,foscarin2024beat}；masked diffusion 通过迭代推断学习解决相互竞争的 output grids \cite{foscarin2026masked}；interval-object 或 reformulated targets 则改变网络的预测对象 \cite{ahn2025beatfcos,bolt2026reformulated}。这些方法所处的部署条件与 CASM 不同：CASM 只改变已冻结 activation stream 的解码方式，不要求改动上游模型。
```

## 为什么推荐这一版

- 开头采用 reading 中最常见的逻辑：先定义任务，再解释其功能，最后引出自动跟踪的一般困难。
- DBN 段明确承认 latent trajectory 会随 observation 改变；全局设定的是状态支持范围与 transition law。
- Introduction 只用 PLPDP 引出尚未解决的问题；local IBI、confidence 和完整 PLP 谱系均留给 Related Work。
- 正文只解释 Fig. 1 的用途；caption 负责描述具体情形，并明确两例都不是 count safeguard fallback。
- 收尾从 decoder policy 的层面解释迁移，不把 CASM 称为 parameter-free，也不声称 semi-Markov 结构天然保证泛化。
