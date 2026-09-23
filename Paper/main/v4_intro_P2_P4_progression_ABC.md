# CASM Introduction P2–P4：从全局约束，到局部调节，再到周期竞争

## 我的推荐

我建议正文先采用 **A 版**。它把方法演进说清楚，同时保留了足够的技术精度：

1. DP、CRF、DBN 都会使用局部 activation，但它们的 temporal model 主要在整首曲目或整个模型层面定义；
2. PLPDP 的关键进步，是让当前段落的 local evidence 同时决定 preferred IBI 和 temporal constraint 的强度；
3. CASM 再向前一步：它不只看当前最强周期有多强，还比较它与最强备选周期之间的差距；
4. 周期胜得越明确，CASM 越敢使用 timing regularity；周期接近打平时，CASM 越依赖 activation；
5. 最终的 Direct fallback 是另一层独立 safeguard，不能与上述 ambiguity-based soft relaxation 混写。

**B 版**最容易读，适合你希望 Introduction 的逻辑一眼就能看懂的情况。**C 版**最精确，适合担心 reviewer 追问 PLPDP confidence、CASM margin 和 fallback 到底分别做什么的情况。

我认为这三段真正应该留下的主线是：

> Earlier decoders use local evidence to select a path within a largely global temporal model. PLPDP lets local evidence also adapt that temporal model. CASM further asks whether the selected local period wins clearly over its strongest alternative.

中文就是：

> 早期 decoder 用局部证据在一个大体全局定义的节奏模型中选择路径；PLPDP 让局部证据也能调节这个节奏模型；CASM 又进一步判断，当前选中的局部周期是否真正明显优于最强备选周期。

这不是从 “temporal model” 走向 “pure local evidence”。更准确的说法是：

> **The shift is from a largely global temporal model to an evidence-conditioned local temporal constraint, and then to an ambiguity-aware one.**

> **这个演进，是从大体全局定义的时间模型，走向由局部证据调节的时间约束，再走向能够感知多种周期竞争的时间约束。**

---

## 技术演进到底发生在哪里

| 问题 | DP / CRF / DBN | PLPDP | CASM |
|---|---|---|---|
| activation 做什么？ | 为不同 beat path 提供 observation evidence | 既为 beat path 提供证据，也用于计算 PLP | 在 activation maxima 上产生候选事件，并为路径提供证据 |
| preferred spacing 从哪里来？ | 来自 track-level tempo、学习到的 sequence potentials，或全局配置的 tempo/meter state model | 从当前段落的 PLP 得到 time-varying IBI | 从候选点附近的局部周期证据得到最佳 period |
| constraint strength 怎样决定？ | 由固定或全局学习的 penalty / transition model 决定 | 由所选 PLP peaks 的高度形成 confidence，并据此调整 DP constraint | 由最佳 period 与最强备选 period 的差距决定 |
| 是否显式检查多种合理 period？ | 通常不以局部 runner-up comparison 的形式检查 | DP confidence 没有显式比较 strongest alternative IBI | 显式比较 best period 与 strongest alternative period |
| 不确定时怎样处理？ | 仍在既定 temporal model 内进行推断 | PLP 较弱时降低 temporal constraint 的作用 | 两个 period 接近时连续减弱 duration constraint，让 activation 更主导 |
| 是否保留多个 tempo path？ | 依具体模型而定 | 否；输出一条 DP path | 否；ambiguity 只调节一条 semi-Markov path 的 duration cost |
| Direct fallback | 无此机制 | 无 CASM 式的最终 beat-count safeguard | 解码完成后，若结构化输出的 beat 数量异常，返回 Direct path |

这里最重要的区别不是 “谁用了 local evidence”。三类方法都用了。区别在于，**local evidence 能不能改变 temporal constraint 本身，以及改变它时有没有检查其他同样合理的周期解释。**

---

## 为什么不需要再放设想表

这个对比用正文就能说清楚，不值得单独占一张表。表格中的数字只能是人为设定的示意分数，容易让 reviewer 误以为它们来自真实模型输出，也会打断 Introduction 的论证节奏。

最简单、最准确的口头解释是：

> A strong best period is not necessarily a clear choice. It is reliable when the strongest alternative is much weaker, but ambiguous when the two are nearly tied.

> 最强周期本身很强，不代表选择已经明确。最强备选周期远弱于它时，这个选择才可靠；两者接近时，当前节拍层级仍然存在歧义。

论文中让 P3 说清这一点，P4 随即说明 CASM 如何计算这个差距并据此调节 constraint，已经足够。下面 MD 中的技术对照表只是我们修改文字时使用的思考工具，不建议放进论文。

---

# A 版：平衡、清楚、适合正文（推荐）

## English

**Paragraph 2**

For post-processors, the central question is how much temporal regularity should influence the local activation evidence. All structured decoders combine these two sources, but they differ in where the temporal rule comes from. Early dynamic programming (DP) used a track-level tempo and penalized inter-beat intervals (IBIs) that departed from it \cite{ellis2007beattracking}. Conditional random fields (CRFs) learned sequence preferences that allow local tempo variation \cite{fillon2015crf}, while dynamic Bayesian networks (DBNs) infer tempo, phase, and meter within globally configured state ranges and transition laws \cite{krebs2015dbn,bock2016joint}. Thus, local evidence changes the decoded path, but the temporal rule itself is not explicitly recalculated from the ambiguity of each passage. This structure improves continuity when its assumptions fit the music, but can suppress useful activation peaks when they do not \cite{ahn2026smcblindspot}.

**Paragraph 3**

PLPDP \cite{chiu2023localperiodicity} changes this division of labor by deriving a time-varying IBI and confidence from predominant local pulse (PLP). The IBI tells the decoder what beat spacing to prefer, while the confidence determines how strongly that spacing should be enforced. Local evidence therefore shapes both the event scores and the temporal constraint. However, PLPDP derives its confidence from the heights of the selected PLP peaks. This indicates how strong the selected pulse is, but does not explicitly ask whether another IBI is almost as plausible. A strong period may be a clear winner, or it may be nearly tied with a half- or double-tempo alternative; these cases call for different levels of temporal commitment.

**Paragraph 4**

We introduce CASM, a context-aware semi-Markov decoder that makes this comparison explicit. At each activation-supported candidate, CASM identifies the strongest local period and its strongest alternative, and measures how far the winner is ahead. When the separation is large, CASM applies a stronger candidate-to-candidate duration constraint, which can recover weak but rhythmically supported beats. When the periods are close, it weakens that constraint and lets the activation evidence play a larger role. This gradual adjustment is separate from a final beat-count safeguard, which returns the Direct path only when the structured output becomes implausibly dense or sparse. CASM searches a sparse graph of activation maxima, and a beat-synchronous meter stage keeps downbeats consistent with the selected beat sequence. It uses the same broad period support for all inputs and requires neither neural-network retraining nor a track-specific tempo or meter estimate.

## 中文

**第二段**

对于后处理器，核心问题是：时间规律应该在多大程度上影响网络给出的局部 activation。所有结构化 decoder 都会结合这两类信息，区别在于时间规则从哪里来。早期的动态规划（DP）先得到整首曲目的 tempo，再惩罚偏离该 tempo 的拍间距（IBI）\cite{ellis2007beattracking}。条件随机场（CRF）通过学习到的序列偏好允许 tempo 在局部变化 \cite{fillon2015crf}；动态贝叶斯网络（DBN）则在全局配置的 tempo 范围、meter 类型和 transition law 之内推断 tempo、phase 和 meter \cite{krebs2015dbn,bock2016joint}。因此，局部证据会改变最终选择的路径，但 temporal rule 本身并不会因为当前段落存在多种合理解释而被重新计算。当这些规则适合音乐时，它们能提高时间连续性；不适合时，也可能压制原本有用的 activation peaks \cite{ahn2026smcblindspot}。

**第三段**

PLPDP \cite{chiu2023localperiodicity} 改变了这种分工。它从 predominant local pulse（PLP）中估计随时间变化的 IBI 和 confidence。IBI 告诉 decoder 当前偏好多远出现一个 beat，confidence 则决定应该多强地维持这个间距。因此，local evidence 不只影响哪些位置像 beat，也开始调节 temporal constraint 本身。不过，PLPDP 的 confidence 来自所选 PLP peaks 的高度。它说明被选中的 pulse 有多强，却没有显式检查另一个 IBI 是否也几乎同样合理。一个很强的 period 可能遥遥领先，也可能与 half-tempo 或 double-tempo 的解释几乎打平；这两种情况不应该产生同样强的节奏承诺。

**第四段**

我们提出 CASM，一个把这种比较显式加入解码过程的 context-aware semi-Markov decoder。在每个由 activation 支持的候选点上，CASM 找出最强局部 period 和最强备选 period，并计算领先幅度。两者差距较大时，CASM 加强候选事件之间的 duration constraint，从而有机会恢复 activation 较弱但节奏上合理的 beat；两者接近时，它减弱该约束，让 activation evidence 发挥更大的作用。这个连续的强弱调节，与最终的 beat-count safeguard 是两套不同的机制：只有当结构化输出的 beat 数量异常过多或过少时，后者才返回 Direct path。CASM 在 activation maxima 构成的稀疏图上搜索，随后由 beat-synchronous meter stage 保证 downbeat 与已选 beat sequence 一致。它对所有输入使用同一个宽广的 period support，不需要重新训练神经网络，也不需要逐曲提供 tempo 或 meter 估计。

## 为什么 A 版最合适

- P2 没有把 DP、CRF、DBN 错写成 “不看 local evidence”，而是准确指出它们没有根据当前段落的 ambiguity 显式重算 temporal rule。
- P3 用两句话说明 IBI 与 confidence 的不同职责，然后把批评集中在 **confidence 没有显式比较备选 IBI**，不会过度声称 PLP 完全看不见歧义。
- P4 先说核心机制，再交代 fallback、sparse graph 和 meter stage。读者不会把 “低 margin” 与 “切回 Direct” 混为一谈。
- 最后一句保留了方法的实用性，但没有声称 CASM 不使用 tempo range。它准确承认 CASM 对所有输入使用同一个 broad support。

---

# B 版：最白话、演进最醒目

## English

**Paragraph 2**

Every post-processor balances two signals: the network indicates where beats may occur, and a temporal model indicates how the beat sequence should behave. In DP, CRF, and DBN decoders, the local evidence always matters, but the temporal model is largely defined at the track or model level---through a track-level tempo, learned sequence preferences, or configured tempo and meter transitions \cite{ellis2007beattracking,fillon2015crf,krebs2015dbn,bock2016joint}. The evidence can lead the decoder to a different path, but it does not explicitly make the temporal rule weaker when the current passage supports several rhythmic interpretations. A well-matched rule prevents missing or repeated beats; a poorly matched one can pull the output away from useful activation peaks \cite{ahn2026smcblindspot}.

**Paragraph 3**

PLPDP \cite{chiu2023localperiodicity} takes an important next step: it uses the current local evidence not only to locate beats, but also to adjust the temporal rule. From PLP, it estimates the current beat spacing, or IBI, and a confidence value. The IBI sets the preferred spacing, and the confidence controls how strongly the decoder follows it. One question is still missing, however: did the chosen beat spacing win clearly? PLPDP measures the strength of the selected PLP peaks, but does not explicitly compare the selected IBI with the strongest alternative. A strong selected period is reliable when the alternative is much weaker, but remains ambiguous when the two are nearly tied. This distinction matters when half- and double-tempo interpretations are both plausible.

**Paragraph 4**

CASM asks this missing question directly: which local period wins, and by how much? It searches a sparse graph of activation peaks and compares the best local period with the strongest alternative at every candidate. A clear winner gives CASM more reason to enforce regular timing and recover a weak beat. A close result gives it less reason, so the path follows the network activations more closely. CASM makes this change gradually rather than switching decoders whenever the rhythm is ambiguous. A separate safeguard returns the Direct path only if the final structured sequence contains far too many or too few beats. Finally, a beat-synchronous meter stage places downbeats on the selected beat sequence. The method requires no neural-network retraining and no track-specific tempo or meter estimate.

## 中文

**第二段**

每个后处理器都在平衡两种信息：网络指出哪些位置可能是 beat，时间模型规定整条 beat sequence 应该怎样变化。DP、CRF 和 DBN 一直都会使用 local evidence；但它们的 temporal model 主要在整首曲目或整个模型的层面定义，例如整曲 tempo、学习到的序列偏好，或者事先配置的 tempo 和 meter transitions \cite{ellis2007beattracking,fillon2015crf,krebs2015dbn,bock2016joint}。证据变化时，decoder 可以选择另一条路径，但它不会因为当前段落同时支持几种节奏解释，就显式减弱 temporal rule。规则与音乐匹配时，它可以防止漏拍和重复；不匹配时，也可能把结果从有用的 activation peaks 拉开 \cite{ahn2026smcblindspot}。

**第三段**

PLPDP \cite{chiu2023localperiodicity} 向前走了重要一步：它用当前的 local evidence 做两件事，不仅寻找 beat，也调节 temporal rule。它从 PLP 估计当前的 beat spacing，也就是 IBI，以及一个 confidence。IBI 决定偏好的拍间距，confidence 决定 decoder 应该多强地遵守这个间距。不过，它还没有直接回答一个问题：当前选中的 beat spacing 究竟赢得有多明显？PLPDP 衡量的是所选 PLP peaks 的强度，却没有显式比较所选 IBI 与最强备选 IBI。最强 period 自身很强，并不代表选择已经明确：备选 period 远弱于它时，这个选择才可靠；两者接近时，当前节拍层级仍然存在歧义。当 half-tempo 与 double-tempo 都说得通时，这个区别尤其重要。

**第四段**

CASM 直接追问这个缺少的问题：哪个 local period 胜出，它领先了多少？它在 activation peaks 组成的稀疏图上搜索，并在每个候选点比较最强 local period 与最强备选 period。winner 明显领先时，CASM 有更充分的理由维持规则的 timing，并补回一个较弱的 beat；两者接近时，它就少相信这个时间规则，让路径更多地跟随网络 activation。CASM 会连续地调节约束强度，而不是一遇到歧义就更换 decoder。另一个独立 safeguard 只在最终结构化结果的 beat 数量明显过多或过少时返回 Direct path。最后，beat-synchronous meter stage 在已选 beat sequence 上放置 downbeats。整个方法不需要重新训练神经网络，也不需要逐曲提供 tempo 或 meter 估计。

## B 版的优点与风险

- 优点是演进非常清楚：**local evidence selects → local evidence adapts → alternatives are compared**。
- “Which local period wins, and by how much?” 很好记，也准确对应 CASM 的核心设计。
- 风险是 P2 对三类传统方法的内部差异压缩得更多。它适合 Introduction，但 Related Work 仍需分别说明 DP、CRF 与 DBN。
- 最后一句若要最严谨，可补上 A 版的 “It uses the same broad period support for all inputs”，避免 reviewer 把 “no track-specific tempo estimate” 误读为 “no tempo support”。

---

# C 版：技术边界最明确、最适合防 reviewer 误读

## English

**Paragraph 2**

Structured post-processors combine framewise activation evidence with a temporal term, but their temporal assumptions are usually specified or learned globally. The Ellis DP decoder penalizes deviations from a track-level tempo estimate \cite{ellis2007beattracking}. CRFs learn sequence potentials that can represent local tempo changes, but those potentials remain fixed at inference time \cite{fillon2015crf}. DBNs infer an observation-dependent tempo--phase--meter trajectory, while their state support, meter set, transition law, and observation--transition balance are configured for the model as a whole \cite{krebs2015dbn,bock2016joint}. These methods therefore adapt the selected trajectory to the input, but do not explicitly adapt the strength of temporal regularization to the local competition between plausible metrical interpretations. A mismatched temporal model can consequently override informative activation evidence \cite{ahn2026smcblindspot}.

**Paragraph 3**

PLPDP \cite{chiu2023localperiodicity} makes the temporal term input-dependent. It replaces a fixed IBI target and penalty weight with a time-varying IBI $\hat{\delta}(n)$ and confidence $\lambda(n)$ estimated from PLP. The former is obtained from the spacing of adjacent PLP peaks and sets the center of the DP timing penalty; the latter is derived from their heights and scales that penalty. This is a substantial shift from a globally fixed constraint to a locally conditioned one. Yet $\lambda(n)$ is a non-comparative measure: it describes the selected PLP peaks without explicitly evaluating the strongest competing IBI. The selected pulse can therefore be locally strong even when a half- or double-tempo interpretation is nearly as well supported.

**Paragraph 4**

We introduce CASM, a context-aware semi-Markov decoder that conditions temporal regularization on explicit period competition. At each retained activation maximum $i$, CASM scores admissible local periods, selects the best period $\tau_i$, and compares it with the strongest alternative outside a small neighborhood of $\tau_i$. Their normalized margin $c_i$ controls the stiffness of the candidate-to-candidate duration cost: a large margin concentrates the cost around the selected period, whereas a small margin broadens and weakens it so that activation evidence has greater influence. The margin is a deterministic local competition score, rather than a calibrated probability, and CASM still decodes a single path rather than preserving multiple tempo hypotheses. After decoding, an independent beat-count safeguard returns the exact Direct path if the structured sequence is implausibly dense or sparse. A beat-synchronous meter stage then selects downbeats from the decoded beats. CASM uses one broad, fixed period and transition support for all inputs; it does not require a track-specific tempo trajectory, meter estimate, or neural-network retraining.

## 中文

**第二段**

结构化后处理器把逐帧 activation evidence 与 temporal term 结合起来，但其中的时间假设通常在全局层面设定或学习。Ellis 的 DP decoder 会惩罚偏离整曲 tempo estimate 的拍间距 \cite{ellis2007beattracking}。CRF 学习能够表示局部 tempo 变化的 sequence potentials，但推断时这些 potentials 已经固定 \cite{fillon2015crf}。DBN 的 tempo--phase--meter 轨迹会随 observation 改变，但它的 state support、meter set、transition law，以及 observation 与 transition 的整体平衡，都是针对整个模型配置的 \cite{krebs2015dbn,bock2016joint}。因此，这些方法会根据输入改变所选轨迹，却不会根据多个合理节拍解释在当前段落中的竞争，显式调节 temporal regularization 的强度。当 temporal model 与音乐不匹配时，它就可能盖过有信息的 activation evidence \cite{ahn2026smcblindspot}。

**第三段**

PLPDP \cite{chiu2023localperiodicity} 让 temporal term 变成 input-dependent。它用从 PLP 估计的 time-varying IBI $\hat{\delta}(n)$ 和 confidence $\lambda(n)$，替代固定的 IBI target 和 penalty weight。前者来自相邻 PLP peaks 的间距，用来设定 DP timing penalty 的中心；后者来自这些 peaks 的高度，用来缩放 penalty 的强度。这是从全局固定约束走向局部条件化约束的重要一步。但是，$\lambda(n)$ 是一个非比较性的量：它描述所选 PLP peaks 本身，却不显式评价最强的竞争 IBI。因此，即使 half-tempo 或 double-tempo 的解释几乎同样合理，所选 pulse 本身仍然可能很强。

**第四段**

我们提出 CASM，一个根据显式 period competition 调节 temporal regularization 的 context-aware semi-Markov decoder。在每个保留的 activation maximum $i$ 上，CASM 对允许的 local periods 评分，选出最佳 period $\tau_i$，再把它与 $\tau_i$ 附近小范围之外的最强备选 period 比较。二者的 normalized margin $c_i$ 控制候选事件之间 duration cost 的刚性：margin 较大时，cost 更集中在所选 period 附近；margin 较小时，cost 变宽、变弱，因此 activation evidence 获得更大的影响。这个 margin 是确定性的局部竞争分数，并不是校准后的 probability；CASM 仍然只解码一条路径，并不保存多个 tempo hypotheses。解码完成后，一个独立的 beat-count safeguard 会在结构化 sequence 异常过密或过疏时返回完全相同的 Direct path。beat-synchronous meter stage 随后从已解码 beats 中选择 downbeats。CASM 对所有输入使用同一个宽广且固定的 period 和 transition support，不需要逐曲提供 tempo trajectory、meter estimate，也不需要重新训练神经网络。

## C 版的优点与风险

- 它最明确地区分了 “selected pulse 的强度” 与 “selected period 相对 runner-up 的领先幅度”。
- 它明确承认 DBN trajectory 会随 observation 改变，避免 “DBN 完全固定” 这种 reviewer 很容易反驳的说法。
- 它明确说明 CASM margin 不是 probability，也没有同时保留多个 tempo hypotheses。
- 风险是符号和术语较多。若 Introduction 已经很密，建议把 P2 和 P3 用 A 版，只把 C 版 P4 的两句技术边界放进 Methodology。

---

## 我建议的最终拼法

如果只选一个整版，我选 **A**。如果允许混合，我建议：

- 用 A-P2，因为它对 DP、CRF、DBN 的表述最平衡；
- 用 B-P3，因为 “did the chosen beat spacing win clearly?” 是最容易让外行理解的中心问题；
- 用 A-P4，并保留 C-P4 的一句边界说明：

> The margin is a deterministic local competition score rather than a calibrated probability, and CASM still decodes a single path rather than preserving multiple tempo hypotheses.

这一混合版的论证顺序会非常稳：

1. 先问 temporal regularity 应该在多大程度上约束 activation；
2. 再说明早期方法的 path 会适应 observation，但 temporal rule 不会根据 local ambiguity 显式调节；
3. PLPDP 让局部证据同时设定 IBI target 和 constraint strength；
4. 指出 pulse strength 不等于 period decisiveness；
5. CASM 用 best-versus-alternative margin 补上这一步；
6. 最后分开交代 soft relaxation、beat-count fallback 和 meter consistency。

---

## 必须守住的 claim 边界

下面这些句子不要写进论文：

- **“Traditional decoders rely only on predefined constraints.”** 他们都使用 observation/local evidence；DP 还可能先从整曲音频估计 tempo，CRF 的 potentials 也可能由数据学习。
- **“DBN does not adapt to the music.”** DBN 的 latent trajectory 会随 observation 改变；真正全局配置的是 state support、meter set、transition law 等模型结构。
- **“PLPDP uses pure local evidence.”** PLPDP 仍然是带 timing penalty 的 dynamic programming，只是 target 和 strength 由局部 PLP 调节。
- **“PLPDP has no confidence or cannot respond to ambiguity.”** 它有 confidence，也可能间接受到 PLP 峰高或多尺度一致性的影响。准确批评是：它的 DP confidence 没有显式比较 strongest alternative IBI。
- **“A half/double-tempo ambiguity always gives PLPDP high confidence.”** 这个结论过强。可以说 selected pulse may remain strong even when an alternative is similarly supported。
- **“CASM keeps several competing tempo paths.”** 当前实现只利用 alternative period 调节一条路径的 duration cost。
- **“Low ambiguity confidence makes CASM switch to Direct.”** 低 margin 只会软化 duration constraint。Direct fallback 由最终 beat-count ratio 独立触发。
- **“CASM has no tempo range or tempo assumptions.”** CASM 仍使用固定且宽广的 period/transition support。安全说法是：它不需要逐曲 tempo estimate 或预先给定的 tempo trajectory。
- **“CASM generalizes better because no retraining is needed.”** “无需重训”是事实层面的机制描述；“generalizes better” 是实验结论，需要可靠、充分的结果支持。

---

## 对当前稿件的具体处理建议

1. 用 A 或混合版替换当前 Introduction 的 P2–P4，删掉正文里的 `(verA)` 和被注释掉的备选段落。
2. 不再加入设想表。让 P3 用 “a strong selected period may still be nearly tied with an alternative” 直接说清 pulse strength 与 period decisiveness 的区别。
3. Introduction 暂时不要列 “good performance on MIREX-style evaluation”“well generalization”“low tuning burden” 等强结论；这些应等待结果表的 provenance 与 operating point 完全统一后再写。
4. “open-source, pip-installable” 只有在匿名审稿政策允许、链接确实可访问、包已发布时再放回贡献列表。它不是解释 CASM 学术贡献所必需的句子。
5. Fig.~\ref{fig:casm-examples} 的 caption 不要再写成 “ambiguity makes CASM defer to Direct”。图中如果展示的是 margin 变低后 timing cost 变弱，就准确写成 soft relaxation；只有实际触发 beat-count safeguard 的例子才能写 Direct fallback。
6. 检查当前稿件中同一张 `p0.jpg` 是否被连续插入两次。

---

## Related Work 应怎样承接

Introduction 只需要建立上述演进，不要在这里把所有历史方法讲完。Related Work 可以用下面的结构展开：

1. **End-to-end alternatives**：说明一些更强的 neural models 尝试减少或取消 post-processing，但它们需要与 base model 一起训练，灵活性和跨模型复用有限。然后说明 DBN 因稳定、通用，仍是最常见的后处理器之一。
2. **Globally structured post-processing**：按 DP → CRF → DBN 的顺序，解释 tempo continuity、local tempo variation、joint tempo--phase--meter inference。
3. **Locally adaptive post-processing**：以 PLP、dPLP、PLPDP 为主线，承认它们已经把局部周期信息引入 decoder。
4. **CASM 的准确位置**：不是第一个使用 local periodicity，也不是第一个考虑多个周期；它的特定贡献，是在 activation-supported sparse semi-Markov decoding 中，用 best-versus-alternative period margin 连续调节 duration constraint，并配套一个独立、可解释的 Direct safeguard。

这样写以后，“Despite increasingly accurate neural activations, most practical systems still rely on structured post-processing” 这类句子确实更适合放在 Related Work 的入口或 end-to-end 段落结尾。Introduction 开头则可以保留更自然的顺序：beat 的作用 → 困难曲目 → activation 与 decoder 的分工 → 上述三阶段演进 → CASM。
