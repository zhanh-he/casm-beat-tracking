# CASM v5.1 小细节修改清单

**审读基线：** `Paper/main/casm_v5.tex` at commit `f8f17e3`<br>
**修订稿：** `Paper/main/casm_v5.1.tex`<br>
**范围：** 语法、术语、LaTeX、交叉引用、可读性和复现信息的局部问题。会改变科学结论的问题单独列在 `casm_v5.1_02_major_errors.md`。

## 总体判断

v5 最值得保留的是叙述节奏：它先提出 local evidence 与 temporal regularity 的平衡，再依次引出 DP、CRF、DBN、PLPDP 和 CASM。问题不是“写得不够复杂”，而是若干地方为了简短而省掉了必要定义，另一些地方则使用了营销式或因果性过强的措辞。v5.1 的处理原则是保留约 70% 的 v5 语言气质，同时把可以直接修正的小问题全部落到 TeX 中。

## 1. LaTeX、标题与命名

| v5 位置 | 问题 | 建议 / v5.1 处理 |
|---|---|---|
| L2--3 | `amsmath` 重复加载。 | 删除第二个 `\usepackage{amsmath}`。 |
| L9、L21 | `xcolor` 先无选项、后带 `[table]` 重复加载，Tectonic 会产生 option clash。 | 只保留 `\usepackage[table]{xcolor}`。 |
| L2 | `hyperref` 使用默认彩色边框，当前 PDF 的引用和网址出现红/青框。 | 独立加载 `\usepackage[hidelinks]{hyperref}`。 |
| L12 | `\showchangestrue` 不适合干净审稿稿。 | v5.1 默认 `\showchangesfalse`；仍保留本地红线开关。 |
| L70 | 标题缺少冠词。 | `CASM: A Context-Aware Semi-Markov Post-Processor for Beat Tracking`。 |
| L72 | `Yaolong Ju$^{1,}$` 多出逗号。 | 改为 `Yaolong Ju$^{1}$`。 |
| L88 | `semi-Markov model` 容易被理解为生成式 HSMM。 | 关键词改为 `semi-Markov decoding`。 |
| 全文 | `Beat This` / `BeatThis` 混用。 | 数据/模型名称统一为 `BeatThis`；普通英文短语不使用该拼法。 |
| 表 3 | `w.DBN`、`w.CASM` 不自然。 | 将来重建表时统一成 `+ DBN`、`+ CASM` 或 `w/ DBN`。 |
| 图浮动 | `figure*` 使用 `[h!]` 在双栏中通常不会按预期放置。 | 若重启机制图，优先使用 `[t]`，并在编译后检查跨栏位置。 |

## 2. Abstract 的局部语言问题

### 2.1 硬语法错误

v5 L84：

> resulting in overrides correct local evidence instead of correcting it

应至少改为：

> causing the decoder to override correct local evidence rather than correct local errors.

v5.1 进一步把整句改成更自然、也更准确的对照：

> These assumptions are effective when they match the recording, but can override valid local evidence under expressive timing or rhythmically complex material.

### 2.2 不要把 DBN 写成完全忽略 observation

原文的 `imposing explicit human-specified global assumptions` 容易产生稻草人效果。更准确的句子是：

> Dynamic Bayesian networks (DBNs), the standard structured post-processors, reduce such errors using globally configured tempo, meter, and transition assumptions.

`globally configured` 指约束的 support、state inventory 和 transition law；DBN 解出的 trajectory 本身仍然由 observation 驱动。

### 2.3 CASM 的核心量要具体命名

不要只写 `estimates local periodicity and ambiguity`。建议：

> CASM estimates a local period and its margin over the strongest competing period, using that margin to adjust the stiffness of an event-to-event duration preference.

这样读者在摘要第一次遇到 CASM 时，就知道 ambiguity 不是抽象的 confidence，也不是一个多假设 posterior。

### 2.4 发布状态用中性措辞

在 license 和 PyPI release 未完成前，不要写 `open-source, pip-installable`。v5.1 使用：

> a reference implementation and a machine-readable configuration

这不削弱可复现性，也不会制造可被简单查证为错误的产品状态主张。

## 3. Introduction 的逐句修改

### 3.1 第一段

v5 L93 的：

> However accurate the neural activations become, direct peak picking makes isolated local decisions...

逻辑正确，但句首略显绝对。推荐：

> Even accurate activations do not by themselves guarantee a coherent event sequence: Direct makes independent local decisions and therefore ignores the periodic context of neighbouring beats.

### 3.2 平衡问题段

v5 L95--96 有人为断行，而且 `may fail to correct` / `may suppress` 可以更紧凑：

> A weak regularity constraint preserves the network's predictions but may leave missed or spurious beats uncorrected. An overly strong constraint can instead suppress valid peaks under expressive timing or rapid local tempo variation.

### 3.3 传统 post-processor 段

- `Early dynamic programming approach` 缺冠词且名词数不一致。
- DBN 句应承认 observation-dependent trajectory。

推荐：

> The dynamic-programming method of Ellis assumes one track-level tempo and penalizes IBIs that depart from it. ... DBNs infer an observation-dependent path through tempo, phase, and meter states, but their tempo support, meter inventory, and transition laws are configured globally.

### 3.4 PLPDP 段的 comma splice

v5 L100：

> However, this confidence is derived from PLP peak heights, it reflects ...

这是 comma splice。推荐整段替换为：

> PLPDP derives a time-varying IBI and confidence from predominant local pulse (PLP), using them to set the centre and weight of its timing penalty. The confidence is based on the heights of the selected PLP peaks: it measures the support of the selected pulse, but does not explicitly measure how decisively that period outranks its strongest competitor.

### 3.5 CASM 段避免营销式贡献标题

v5 的 `Low tuning burden`、`Good generalization`、`Open and ready to use` 不是同一层级的科学贡献，而且分别受实验公平性、因果归因和发布状态限制。建议把贡献压成三项：

1. `Comparative local evidence`：best-versus-alternative margin；
2. `Sparse segmental decoding`：candidate-event duration cost + 独立 safeguard/downbeat stage；
3. `Frozen deployment`：一个全局配置、无需神经网络重训或 per-track BPM 输入。

### 3.6 术语强度

| 原词 | 问题 | 推荐词 |
|---|---|---|
| `enforces strict temporal regularity` | 像 hard constraint；代码使用 soft cost。 | `applies stronger temporal regularization` |
| `tempo hypotheses` | CASM 比较局部 lag，不维护完整 tempo trajectory。 | `period hypotheses` / `alternative lags` |
| `periodicity ambiguity` | 可保留作高层概念，但公式处不够具体。 | `period-separation margin` |
| `constraint strength` | 与 width/tolerance 混在一起。 | 高层用 `duration stiffness`，公式分别用 `\sigma(c)` 与 `w(c)` |
| `support` | 容易同时指 PLP evidence 和 BPM range。 | evidence 用 `support/salience`；范围用 `fixed BPM support` |

## 4. Methodology 的局部可读性与复现修复

### 4.1 subsection 标题

`CASM Overview` 改成 sentence case：`CASM overview`。

### 4.2 candidate 与 node score 必须区分

v5 只写 `clipped evidence score $e_i$`。准确实现是：

```tex
e_i=\operatorname{clip}(z^{\mathrm b}_{t_i}/T_z,-L,L).
```

即：

- sigmoid probability 用来找 candidate 和应用 `0.03` threshold；
- temperature-scaled、clipped logit 用作 path node score。

这不是大改算法，但不写清楚就无法复现。

### 4.3 先用一句白话再给 autocorrelation 公式

推荐过渡句：

> To estimate the local period, CASM compares a centred activation window with lagged copies of itself.

然后再给 (q_i(\ell))。这样保留 v5 的人类可读性，同时恢复 v3 的技术完整性。

### 4.4 semi-Markov 的限定句

推荐：

> This variable-duration segment score is the precise sense in which CASM is semi-Markov. CASM is not a generative hidden semi-Markov model, and its segment potentials are hand-specified rather than learned.

这两句可以提前化解“semi-Markov 是否只是重新命名”的 reviewer 质疑。

### 4.5 strength / width 写成三行更好读

不要把一切藏进 (g(c))。写成：

```tex
\sigma(c)=\sigma_0+(1-c)\sigma_u,
\qquad
w(c)=\frac{\lambda c}{2\sigma(c)^2},
\qquad
D_{ij}=w(c_{ij})\log^2\!\frac{\Delta_{ij}}{\bar\tau_{ij}}.
```

随后用一句话解释：

> A small margin both broadens the tolerated timing deviation through (\sigma(c)) and reduces its weight through (w(c)).

### 4.6 downbeat 规则不能只写 `strongly disagrees`

应至少给出：

- allowed meters: 2--7 beats per bar；
- meter-change penalty 的存在；
- Direct downbeat peaks snapped to selected beat grid；
- agreement statistic: event F-measure；
- tolerance: 70 ms；
- fallback threshold: 0.6。

v5.1 已补入这些固定细节。

### 4.7 明确 offline scope

8-s centred window 使用未来帧，完整 path 也在整段输入上 backtrack。因此用一句干净的：

> All decoders are evaluated offline.

不要使用 v5 L247 的：

> the future information is accessible for model to top up the estimate accuracy.

## 5. Experiments 的局部语言修复

| v5 位置 | 原问题 | 推荐写法 |
|---|---|---|
| L238 | `is widely recognized as the hard one` 口语且不严谨。 | `contains deliberately challenging excerpts and provides beat, but not downbeat, annotations` |
| L240 | `accept the 30s the unified` 双重冠词。 | `accept the unified 30-s log-Mel input` |
| L240 | TCN 长句中 `which` 指代不清。 | 拆为两句，分别说明 reimplementation、input adaptation、tempo head removal。 |
| L242 | 漏掉归档 evaluator 的前 5 s trimming。 | `the first 5 s of each recording are excluded before scoring` |
| L247 | `As we defined our task is offline...` 不通。 | `All decoders are evaluated offline.` |
| L247 | 比较列表没有 CombFilter，后句却说运行 CombFilter。 | 要么恢复有 provenance 的 CombFilter 行，要么全文删除；v5.1 采用后者。 |
| L249 | `many SMC data are fall below` 语法错误。 | `many SMC excerpts contain reference beat rates below 55 BPM` |
| L249 | `with all other ... remain unchanged`。 | `with all other ... remaining unchanged` |
| L260 | `the CASM improves BeatThis ... pick-peaking ... every reported metrics` 多处语法问题。 | 数值重建后再写：`With the frozen ... configuration, CASM improves on Direct for ...`；不可先保留 universal claim。 |

## 6. 表格与结果段的表述细节

即使数值 provenance 修好，表注仍需包含以下信息：

1. Direct 行是 absolute score，其他行是相对同一 Direct 的 percentage-point delta；
2. backbone checkpoint / seed 或 fold aggregation policy；
3. decoder 名称、BPM support、config hash；
4. evaluator、first-5-s trim、piece-macro aggregation；
5. GTZAN 是 independent prespecified aggregate、three-seed summary，还是 post-hoc diagnostic。

表内 ablation 名称也要与方法公式一一对应：

- `Local target, fixed precision`：明确固定了哪个 (\sigma) 或 (w)；
- `Strength only`：明确仅保留 (c) 的 numerator multiplier；
- `Width only`：明确仅让 (c) 改变 (\sigma(c))；
- `One endpoint`：说明使用 start 还是 end context；
- `No safeguards`：说明移除 count safeguard、downbeat agreement safeguard，还是两者。

## 7. Figure 和引用的小错误

- v5 L203--209 将 `fig:casm-response` 整段注释，L211--214 仍引用，当前 PDF 明确显示 `Figure ??`。
- 不能简单恢复旧 `p1.jpg`：它来自 `duration_sigma=0.12` 的历史配置；当前 7F 为 `0.15`。详细原因见大错误文件。
- v5 Fig. 1 的 `defer to Direct` 应改为 `the structured path coincides with Direct without invoking the count-ratio fallback`。
- 代表性 track/window 是 post-hoc 选择，caption 应说明它用于 mechanism illustration，不用于估计平均性能。
- reference IBI 只用于解释，从未输入 decoder；这句应保留。

## 8. Conclusion 与致谢

v5 L510 的 `The next version should...` 像内部备忘录，而且列出的 PLPDP / mechanism ablation 已出现在正文。改成正常 limitation：

> A limitation of the present study is that decoder calibration is not strictly nested for the aggregate SMC estimate. Future work will examine nested or leave-one-dataset-out calibration, matched-support baselines, explicit safeguard statistics, and additional trackers with compatible activations.

致谢改成过去时：

> Computational resources were provided by the SongShan Lake HPC Center (SSL-HPC) at Great Bay University.

## 9. 建议固定的全文词汇表

| 数学对象 / 概念 | 固定英文 |
|---|---|
| (\tau_i) | local period |
| (c_i) | period-separation margin |
| (\sigma(c)) | ambiguity-dependent tolerance |
| (w(c)) | duration stiffness / duration coefficient |
| (D_{ij}) | segment-duration cost |
| 30--300 BPM | fixed broad BPM support |
| 独立峰值基线 | Direct |
| 高层作用 | temporal regularization |
| count safeguard 行为 | returns the exact Direct path |
| 小 margin 行为 | moves toward activation-dominated sparse-path decoding |

这套词汇能避免 `confidence`、`support`、`ambiguity`、`constraint strength` 在不同段落里互相换义。
