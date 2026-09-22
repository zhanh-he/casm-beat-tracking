# CASM 引言第 3-4 段：中文 A/B/C 版本

## 建议

**推荐 A 版，且已将其英文稿写入 `casm_v4.tex`。** 它最完整地保留了下面这条技术叙事，同时没有把引言写成方法章节：

> 全局预设的时间约束 -> PLPDP 对目标周期和约束权重的局部自适应 -> CASM 基于相对歧义间隔的自适应与稀疏片段搜索。

CASM 的核心区别不能写成“首次使用局部置信度”或“首次在不可靠时减弱时间先验”，因为 PLPDP 已经实现了这两点。真正站得住的区别是**条件信号的语义**：

- PLPDP 根据 PLP 曲线相邻峰之间的距离得到局部 IBI，并根据两峰的平均高度得到置信度。DP 条件接收的是已选 IBI 与这个不比较备选解释的强度量。
- CASM 在每个保留的 activation 局部极大值处，计算所有允许 lag 的局部自相关响应；它选择最佳 lag，并计算该分数与一个小邻域之外最强备选分数之间的归一化间隔。这是相对分离度。
- CASM 不保留多条 tempo 路径。备选 lag 只用于判断：围绕已选周期的 duration cost 应该有多“硬”。较小的间隔会减弱时间代价，但本身不会触发 Direct fallback。

## 措辞背后的技术比较

| 维度 | PLPDP | CASM |
|---|---|---|
| 局部周期 | 默认实现分别用 1、3、5 秒尺度下 Fourier tempogram 的主导分量合成 PLP 曲线，将三条曲线相乘，再以相邻 PLP 峰间距作为局部 IBI。 | 在每个 activation 峰候选位置，对允许范围内的 lag 计算归一化局部自相关；最佳 lag 即局部周期。 |
| 条件信号 | $\lambda(n)$ 是两个相邻 PLP 峰的平均高度。它反映已选脉冲曲线的强度/一致性，但没有显式的 runner-up 比较。 | $c_i$ 是最佳 lag 分数与 $\pm2$ lag 帧邻域之外最强分数之间的截断归一化间隔；它衡量已选解释相对竞争解释的分离度。 |
| 在时间项中的作用 | $\hat{\delta}(n)$ 确定 log-IBI 惩罚的中心，$\lambda(n)$ 在当前 DP 帧对惩罚进行缩放。 | 对每条边，将两端的周期与间隔分别作几何平均；间隔同时通过乘法因子和随歧义变化的尺度作用于 log-duration cost。 |
| 搜索空间 | 稠密帧级动态规划可以在任意帧放置节拍。 | 稀疏 semi-Markov 动态规划只在保留的 activation 极大值上选路径；一条边对应一个完整的节拍间片段。 |
| “歧义”的含义 | 歧义可能间接降低 PLP 峰高，但 DP 条件不会显式比较竞争周期的分数。 | 竞争由“最佳对备选”的间隔显式概括；但 CASM 仍是单周期、单路径解码器，不是完整的多假设 tempo inference。 |
| Fallback | PLPDP 的递推允许从当前帧重新开始。 | CASM 的 DP 也可重新开始；此外，只有最终 CASM/Direct 节拍数比例超出固定范围时，才单独返回 Direct 路径。 |

实现依据：[CASM 的局部 lag 评分与间隔](https://github.com/zhanh-he/casm-beat-tracking/blob/paper-revisions/src/casm_beat_tracking/decoder.py#L98-L179)、[CASM 的稀疏边代价](https://github.com/zhanh-he/casm-beat-tracking/blob/paper-revisions/src/casm_beat_tracking/decoder.py#L294-L344)、[PLPDP 的 IBI/置信度构造](https://github.com/SunnyCYC/plpdp4beat/blob/main/modules.py#L80-L140)以及 [PLPDP 的递推](https://github.com/SunnyCYC/plpdp4beat/blob/main/modules.py#L180-L253)。

源码层面的注意事项：PLPDP 论文把 $\lambda(n)$ 定义为随时间变化的量；其参考代码会缓存加权后的 penalty，只有整数局部 IBI 发生改变时才更新 confidence factor（[第 224-230 行](https://github.com/SunnyCYC/plpdp4beat/blob/main/modules.py#L224-L230)）。因此，如果某一分段只改变 confidence 而整数 IBI 不变，缓存不会更新。引言仍依据论文公开的算法定义来表述，因为 CASM 的核心区别不应依赖这一实现细节。

## A 版——技术边界最完整（推荐）

### 第 3 段

> PLPDP~\cite{chiu2023localperiodicity} 代表了迈向局部自适应后处理的重要一步。它将主导局部脉冲（predominant local pulse, PLP）转换为随时间变化的 IBI $\hat{\delta}(n)$ 和置信度 $\lambda(n)$：前者确定 tempo-consistency penalty 的中心，后者依据相邻 PLP 峰的平均高度对该惩罚进行缩放。因此，PLPDP 已经同时调整了时间约束的目标和强度。不过，它的置信度是一种不比较备选解释的度量：动态规划条件中没有显式项衡量已选周期相对于竞争周期究竟领先多少。因此，当半速与倍速等假设获得相近的局部支持时，它们之间的相对不确定性仍可能是隐含的。

### 第 4 段

> 我们提出 CASM，一种将上述比较显式化的 context-aware semi-Markov 后处理器。在每个保留的 activation 极大值处，CASM 为所有允许的自相关 lag 评分，选择最强 lag 作为局部周期，并计算它与一个小 lag 邻域之外最强备选项之间的归一化间隔。这个间隔不是经过校准的概率，也不会形成多假设 tempo 路径；它通过一个乘法权重和一个随歧义变化的尺度，控制以已选周期为中心的 duration cost 的刚度。对每个连接候选事件的片段，CASM 综合片段两端的周期与间隔。若最佳解释明显领先，较强的 duration preference 可以恢复较弱但受 activation 支持的节拍；若间隔较小，该 preference 会被压平，使周期性尚未消解时由 activation 证据占主导。图~\ref{fig:casm-examples} 展示了这两种工作状态。确定性的节拍数 safeguard 与 beat-synchronous meter 阶段进一步稳定输出。CASM 与上游模型无关，无需重新训练神经网络，并以可通过 pip 安装、具有 madmom 风格 activation 接口的参考实现提供。

选择 A 版的理由：它写清了 PLPDP 的实际变量，抓住“不比较的峰高”与“相对备选的间隔”之间的差别，并明确把 CASM 的主张限制在单路径歧义门控上。

## B 版——读者优先

### 第 3 段

> PLPDP~\cite{chiu2023localperiodicity} 是从固定后处理走向局部自适应后处理的重要桥梁。它从主导局部脉冲（PLP）中同时提取局部 IBI 与置信度，前者设定偏好的节拍间隔，后者缩放时间惩罚。因此，PLPDP 已经能够判断所选脉冲是否足够强；但它没有显式追问，这个脉冲相对另一个合理周期究竟领先多少。当半速与倍速等解释都能拟合局部 activation 模式时，这一点尤为重要：已选脉冲可以十分显著，但节拍层级的解释仍未必唯一。

### 第 4 段

> CASM 用 ambiguity-conditioned semi-Markov 后处理器来处理这个差别。它在每个保留的 activation 峰附近，比较最佳局部自相关 lag 与一个小 lag 邻域之外最强备选项，并将两者的相对间隔转换为事件间 duration preference 的刚度。因此，当某个局部周期清晰胜出时，CASM 会施加足够强的规则性以恢复较弱但受 activation 支持的节拍；当没有周期明确胜出时，则更多依赖 activation 证据。搜索仍然是在观测极大值上进行的单条稀疏路径，而不是多假设 tempo 模型；Direct 仅由独立的节拍数 safeguard 使用。图~\ref{fig:casm-examples} 展示了两种工作状态。由此得到的后处理器是确定性的、与上游模型无关、无需重新训练神经网络，并以可通过 pip 安装、具有 madmom 风格接口的参考实现提供。

选择 B 版的理由：它先提出概念问题，再介绍实现细节，对节拍跟踪领域之外的读者更友好。

## C 版——紧凑 camera-ready

### 第 3 段

> PLPDP~\cite{chiu2023localperiodicity} 从主导局部脉冲（PLP）中推导随时间变化的 IBI 与置信度，使后处理具有局部自适应能力。IBI 设定动态规划惩罚的目标，而置信度——相邻 PLP 峰的平均高度——设定其权重。这一置信度衡量已选脉冲，却不显式将其与竞争周期解释进行比较，因此半速/倍速竞争等相对歧义仍然是隐含的。

### 第 4 段

> 我们提出 CASM，一种以这一缺失比较为条件来调节时间规则性的稀疏 semi-Markov 后处理器。在每个 activation 峰候选位置，CASM 以最佳局部自相关 lag 作为周期，并用其相对一个小 lag 邻域之外最强备选项的归一化间隔，控制候选事件间 duration cost 的刚度。分离度清晰时，局部规则性增强；分离度较弱时，activation 证据占主导，但这不意味着 CASM 进行多假设 tempo inference，也不意味着它会自动回退到 Direct。图~\ref{fig:casm-examples} 展示了两种状态。CASM 是确定性的、与上游模型无关、无需重新训练，并以可通过 pip 安装、具有 madmom 风格 activation 接口的参考实现提供。

选择 C 版的理由：它以最小篇幅保留了准确的 novelty 边界。

## 有意删除或收窄的主张

- 删除“PLPDP 只调整局部 tempo”的说法，因为它也调整惩罚权重。
- 用“PLP 峰高”与“最佳对备选的分离度”这一精确差别，替代泛化的 confidence 表述。
- 不声称 CASM 保留多条 tempo 假设或解决 metric-level switching。
- 将半速/倍速竞争作为例子，而不是 CASM 唯一考虑的备选关系或已经解决的错误模式。
- 不声称高歧义会自动让 CASM 返回 Direct；只有独立的节拍数比例 safeguard 会这样做。
- 不把“target、strength、tolerance”写成三个彼此独立的控制量；准确说法是，一个 margin 通过乘法因子和随歧义变化的尺度共同改变 duration cost 的刚度。
- 删除缺少证据的 MIREX 泛化主张，以及“CASM 在结构上必然比 DBN 更少调参”的因果主张。
- 将“compatible with madmom”收窄为与当前实现一致的“madmom-style activation interface”。
- 因为公开仓库仍把 license 选择与首次 PyPI 发布列为待办，将“已作为开源软件发布”收窄为“提供参考实现”。
