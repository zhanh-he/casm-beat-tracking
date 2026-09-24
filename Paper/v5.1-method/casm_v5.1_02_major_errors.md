# CASM v5 深度审读：阻断级错误与修复路线

**审读基线：** `Paper/main/casm_v5.tex` at commit `f8f17e3`<br>
**证据范围：** 当前 release decoder/config、v3 原始方法描述、Frozen-4F mechanism bundle、Frozen-7F release 文档与结果表、v4 provenance audit<br>
**结论：** v5 的语言可作为风格基线，但当前结果表、ablation、机制图和 calibration claim 不能共同代表一个统一的 7F 实验。以下项目在投稿前属于 P0/P1 阻断项。

## 一页结论

1. **主结果表仍含可逐格证明的 CASM/DBN block 错配。** 它不是“可能舍入错”，而是 MSCNN/TCN 的 SMC 三元组在方法之间发生了精确交叉贴错；同一行的 GTZAN block 又来自其他 range 或 operating point，形成 Frankenstein rows。
2. **ablation 表把 4F variants 与另一条 full-CASM row 放在一起。** 五个变体来自 `duration_sigma=0.12` 的历史 Frozen-4F bundle；表首 full row 既不是该 4F full model，也不匹配当前 `duration_sigma=0.15` 的 Frozen-7F release。
3. **p0/p1 机制图是 4F response law，正文却按 7F 解释。** p1 在 (c=1) 处约为 138.9；7F 正确上限应为 88.9。p0 的最终 beat path 在两个样例上碰巧与 7F 一样，但橙色 (w(c_i)) 仍是旧配置。
4. **CASM/DBN calibration sensitivity 不是 matched experiment。** CASM 每个 fold subset 使用多数据集 BeatThis inventory，DBN 使用 SMC-only；样本量、objective、search space 都不同。因此只能描述两个 selection pipeline 的现象，不能推出 CASM 这个 decoder class 天生较稳定。
5. **PLPDP--CASM 区别必须收紧。** PLPDP 已经同时使用 local IBI 和 time-varying confidence；CASM 的核心新增不是“第一次 local/confidence-aware”，而是 best-versus-strongest-alternative lag margin、sparse candidate graph、endpoint-symmetric segment cost 和独立 safeguards。
6. **ambiguity relaxation 与 Direct fallback 是两个机制。** 小 margin 只使 soft duration term 变弱；exact Direct 仅由 count-ratio safeguard 返回。
7. **当前 release 只足以报告锁定的 BeatThis--CASM 结果。** GTZAN clean three-seed refresh、MSCNN/TCN Frozen-7F refresh 均仍 pending。v5.1 因此采用 audit-safe 策略：保留可追溯 CASM absolute results，隔离所有无法绑定唯一 manifest 的比较表。

---

## P0.1 主结果表存在确定的 provenance 错配

### 证据

v5 L316--351 延续了旧表污染。与已审计 Frozen-7F archive 对照：

| Backbone | v5 行标签 | v5 SMC `F1/CMLt/AMLt` | 归档中真正身份 |
|---|---|---:|---|
| MSCNN | CASM, 30--300 | `+0.3/+3.5/+6.8` | DBN, 30--300 |
| MSCNN | DBN, 30--300 | `-0.2/+2.2/+4.1` | CASM, 55--215 |
| TCN | CASM, 30--300 | `+1.7/+4.5/+8.2` | DBN, 30--300 |
| TCN | DBN, 30--300 | `-0.4/+2.1/+5.9` | CASM, 55--215 |

四个三元组均逐格一致，且在两个 backbone 上重复同一交换模式；无法解释为随机误差或一位小数舍入。

更严重的是，这并非两条完整 row 简单互换。例如 TCN/CASM 的 GTZAN 六格对应旧 CASM narrow block，而 SMC 三格对应 DBN wide block，最后却标为 `CASM 30--300`。该行不对应任何一次完整实验。

BeatThis CASM row 也不是当前 Frozen-7F wide result：旧 v5 写 `GTZAN Beat +0.3/+0.8/+1.2`，已审计 7F wide 约为 `0.0/+0.4/+0.6`；SMC AMLt 也不同。

详细历史证据见：

- [`2026-09-22_v4_table_calibration_dp_plpdp_explainer.md`](../notes/2026-09-22_v4_table_calibration_dp_plpdp_explainer.md)
- [`2026-09-22_casm_tempo_range_and_methodology_audit.md`](../notes/2026-09-22_casm_tempo_range_and_methodology_audit.md)

### 为什么不能手工换回三格

因为 GTZAN block、range identity、checkpoint aggregation 和 full operating point 仍不统一。只换 SMC 三格会留下其余错误，并继续无法回答“这一行来自哪个 config hash / seed / evaluator”。

### 正确修复

从 piece-level artifact 重新生成整表，并令每行 metadata 至少包含：

```text
backbone checkpoint(s)
activation cache manifest
decoder + BPM support
CASM/DBN config hash
trim_seconds + evaluator version
piece set + aggregation rule
absolute Direct row + unrounded delta
```

生成脚本应自动检查：

- label 与 metadata 一致；
- delta 可由未舍入 absolute score 重算；
- 同一个三元组没有异常跨方法复用；
- 30--300 / 55--215 block 不会混入同一行；
- 表、abstract、SOTA row 使用同一个 operating point。

### v5.1 当前处理

不展示该表，不尝试手改。源中的旧表放在 `\iffalse` 内仅供 forensic comparison；PDF 只展示可追溯的 release-validated CASM absolute scores。

---

## P0.2 Ablation 表混用 Frozen-4F 与其他 full row

### 可逐格复现的来源

v5 L387--401 的五个 variants：

- `Local target, fixed precision`
- `Strength only`
- `Width only`
- `One endpoint`
- `No safeguards`

逐格来自：

- [`self-run-figures/figures-20260904-1443/data/aggregate_metrics.csv`](../../self-run-figures/figures-20260904-1443/data/aggregate_metrics.csv)
- [`self-run-figures/figures-20260904-1443/data/protocol.json`](../../self-run-figures/figures-20260904-1443/data/protocol.json)

该 bundle 的 frozen parameter SHA 为：

```text
251c96b23223b2e4ddef7f4ab85592663a1c27fcd6d62b1a5d1ef5625ed01f71
```

其关键参数为 `duration_sigma=0.12`，属于历史 Frozen-4F mechanism experiment。

然而 v5 的 `CASM (default, 30--300 BPM)` 行不是同一 bundle 的 full CASM：

| Panel | 同一 4F bundle 的真实 full CASM delta | v5 表首行 |
|---|---:|---:|
| GTZAN Beat | `+0.1/+0.3/+0.3` | `+0.3/+0.8/+1.2` |
| SMC Beat | `+0.2/+2.3/+2.7` | `+0.3/+2.4/+3.6` |

它也不匹配当前 Frozen-7F release：

```text
candidate hash:
93f40ad87602ae68d84c6d1d72e307c27a67cc94d2b508f619f3376df08ae7de
duration_sigma=0.15
```

已审计 7F delta 约为 GTZAN `0.0/+0.4/+0.6`、SMC `+0.2/+2.4/+2.6`，仍与 v5 full row 不同。

### 为什么结论无效

Ablation 的因果对比要求 full model 与 variant 只改变一个声明中的组件。当前表同时改变了 base configuration / operating point，因此 v5 L360 关于 `strength`, `width`, `fixed precision`, `safeguard` 的 component-level 结论不能由表支持。

### 二选一修法

**推荐：** 在同一 Frozen-7F activation/evaluator manifest 下重跑 full 和所有 variants。<br>
**可接受的探索性备选：** 整张表完全恢复成 4F bundle，包括正确 4F full row，并在标题中明确 `exploratory Frozen-4F mechanism study`。此表不能再解释为 release 7F 的 ablation。

---

## P0.3 p0 / p1 机制图不是 release 7F 图

### p1 的硬数学证据

图中响应系数为：

\[
w(c)=\frac{\lambda c}{2[\sigma_0+(1-c)\sigma_u]^2}.
\]

在 (c=1)、(\lambda=4) 时：

- 历史 4F `sigma=0.12`：(4/(2\cdot0.12^2)=138.9)，与 p1 右端约 139 一致；
- release 7F `sigma=0.15`：(4/(2\cdot0.15^2)=88.9)。

因此 p1 不是只差 caption，而是整条 response curve 和真实 edge operating-point distribution 都属于旧配置。

### p0 的细微情况

p0 的两个代表样例在当前 7F decoder 下，最终 beat outputs 与历史图碰巧相同；这只能说明这两条 path 对 `0.12→0.15` 不敏感。图内橙色 (w(c_i)) 仍按 4F 计算，不能说它展示 release 7F 的作用强度。

### 修复

用 current release config 和同一 trace manifest 重生成：

1. (c_i)、(w(c_i))、provisional path、fallback flag；
2. p1 全部 edge coefficient ECDF / per-piece summary；
3. caption 写明 post-hoc track/window selection；
4. caption 区分 `soft relaxation` 与 `count-ratio fallback`。

v5.1 在重生成前不渲染 p0/p1，也不留下 undefined figure reference。

---

## P0.4 GTZAN、MSCNN、TCN 的 release 状态与 v5 结论冲突

当前 [`docs/RESULTS.md`](../../docs/RESULTS.md) 明确记录：

| Backbone / panel | 当前状态 |
|---|---|
| BeatThis 8F, 4556 pieces | Frozen-7F locked and validated |
| BeatThis / SMC, 217 pieces | Frozen-7F locked and validated |
| BeatThis / GTZAN | 仅保留 post-hoc-selected `final1`，clean three-seed refresh pending |
| MSCNN-lite | eight-fold cache recreation 和 GTZAN refresh pending |
| TCN | Frozen-7F refresh / checkpoint recovery pending |

因此下列 v5 结论目前不成立为 release-validated claim：

- abstract：`improves ... across BeatThis, MSCNN, and TCN on GTZAN`；
- abstract：`state-of-the-art performance on SMC`；
- Results：`every reported metric across all three backbones and both datasets`；
- SOTA 表中的 CASM row 被当作统一的 current result。

v5 SOTA row 也与当前 release 文档不一致：

- v5 SMC：`63.0/53.8/64.6`；当前 217-piece macro：`62.9/53.7/63.5`；
- v5 GTZAN：`89.4/80.6/91.0` 等；当前 `final1` diagnostic：Beat `89.5/81.1/90.6`，Downbeat `79.1/71.5/85.3`。

并且 `final1` 是按 GTZAN Beat F post hoc 选出的单点，不能包装成 independent test 或 mean±SD。

### v5.1 当前报告的唯一数值层级

| Panel | Beat F1 / CMLt / AMLt | Downbeat F1 / CMLt / AMLt |
|---|---:|---:|
| BeatThis 8F, all 4556 pieces | `89.5/80.0/87.8` | `86.8/77.0/85.0` over 3744 annotated pieces |
| SMC, 217 pieces | `62.9/53.7/63.5` | unavailable |
| GTZAN `final1` diagnostic | `89.5/81.1/90.6` | `79.1/71.5/85.3` |

这些是 CASM end-to-end absolute results，不是 post-processor superiority evidence。

---

## P0.5 Calibration population 与 sensitivity claim 写错

### v5 的错误描述

v5 L252 写：

> calibrated once on the union of SMC folds 1--7

归档实际的 CASM 7F inventory 是按 BeatThis folds 1--7 过滤、`subset_dataset=null`：

- 3,985 tracks；
- 18 datasets；
- 其中 190 首 SMC。

DBN calibration 才是 SMC-only。

### 两条 pipeline 的关键不匹配

| Scale | CASM calibration inventory | DBN calibration inventory |
|---|---:|---:|
| 1F | 562--575 首，多数据集 | 27--28 首，SMC only |
| 2F | 1129--1148 首，多数据集 | 54--55 首，SMC only |
| 4F | 2267--2287 首，多数据集 | 108--109 首，SMC only |
| 7F | 3985 首，多数据集 | 190 首，SMC only |

此外：

- CASM selection objective 综合多 target、多 metric 与 guards；
- DBN 先最大化 SMC Beat F1，再以 CMLt/AMLt tie-break；
- CASM sensitivity experiment 固定 30--300 support；
- DBN search 允许在 30/55 lower bound、215/300 upper bound 与 13 个 transition weights 中选择。

固定同一个 SMC-fold-0 / GTZAN evaluation panel 是优点，但不能消除以上 calibration population、objective、sample size 和 freedom 的混杂。

### 允许与不允许的表述

**允许：**

> Under their respective, unmatched calibration procedures, the selected CASM configurations exhibited a narrower descriptive spread than the selected DBN configurations.

**不允许：**

> CASM is less sensitive than DBNs to calibration data.

或：

> DBN over-specialises because of its decoder structure.

后两句需要 matched calibration inventory、matched objective、matched support/search budget 和 outer-fold rotation 才能支持。

---

## P1.1 PLPDP--CASM 的本质区别被写成错误的 `strength vs ambiguity`

### PLPDP 已经做了什么

PLPDP 已经从 PLP 推出：

- time-varying local IBI；
- time-varying confidence；
- local IBI 设 timing penalty centre；
- confidence 设 timing penalty weight。

因此不能写：

- CASM 是第一个 local/confidence-aware post-processor；
- PLPDP 只改变 target、不改变 strength；
- CASM 的 novelty 只是“low confidence 时减弱 constraint”。

### 代码支持的本质区别

| 维度 | PLPDP | CASM |
|---|---|---|
| 搜索域 | dense frames | retained activation maxima 的 sparse graph |
| period estimator | PLP peak spacing / local pulse representation | local normalized autocorrelation lag bank |
| conditioning signal | selected PLP peaks 的 height/salience | best lag 相对 strongest non-neighbouring alternative 的 normalized margin |
| transition context | 当前 frame 的 local quantities | edge 两端的 geometric-mean period 与 margin |
| cost modulation | local target + confidence weight | margin 同时改变 multiplicative weight 与 tolerance scale |
| output能力 | 可在 dense frame grid 上选位置 | 只能选择 retained candidate maxima |
| safeguards | PLPDP 自身规则 | CASM count-ratio Direct fallback + beat-synchronous downbeat fallback |

最准确的一句话：

> PLPDP uses PLP-peak salience to weight a dense-frame local-IBI penalty; CASM instead uses an explicit best-versus-strongest-alternative lag margin to scale a sparse candidate-to-candidate duration cost.

### 重要边界

CASM 当前不维护多个 tempo trajectories。它先取 argmax lag，再保留一个 scalar margin。`half/double tempo` 是 competing lag 的例子，不代表方法完成了 multi-hypothesis inference，也不保证解决 metrical-level switching。

---

## P1.2 `ambiguity → Direct` 是错误机制解释

代码中的两条独立链路：

### Soft ambiguity conditioning

\[
D_{ij}=
\frac{\lambda c_{ij}}
{2[\sigma_0+(1-c_{ij})\sigma_u]^2}
\log^2\!\left(\frac{\Delta_{ij}}{\bar\tau_{ij}}\right).
\]

当 (c_{ij}\to0) 时，soft duration cost 变弱。但以下仍然存在：

- candidate threshold；
- sparse candidate topology；
- 30--300 BPM hard edge support；
- node-score optimization；
- restart/backtrace。

因此 path 只是更 activation-dominated，不自动等于 Direct。

### Exact Direct fallback

只有当：

\[
|\pi_{\mathrm{CASM}}|/|\pi_{\mathrm{Direct}}|
\notin[0.85,1.8]
\]

才返回 exact Direct path。

v5 Fig. 1 右侧 `smc_287` 的 `beat_fallback=False`；CASM 与 Direct 碰巧一致，不是“因 ambiguity 触发 fallback”。

---

## P1.3 Tempo support 不是“没有 tempo assumption”

30--300 BPM 在代码中同时：

1. 定义 local autocorrelation 的 admissible lag bank；
2. 硬性筛掉 candidate graph 中不合法的 edges。

扩大范围还会引入新的 runner-up lag，改变 (c_i)。所以范围不是显示参数，也不是仅用于极端 sanity check。

允许写：

> CASM requires no per-track BPM estimate or tempo trajectory prior, but uses one broad fixed local-period and transition support for all inputs.

不允许写：

> CASM requires no tempo range / imposes no tempo assumptions.

---

## P1.4 v5 Methodology 过度压缩，无法复现

必须恢复：

1. (e_i=\operatorname{clip}(z^{\mathrm b}_{t_i}/T,-L,L))；
2. (q_i(\ell)) 的 normalization、8-s centred window、zero padding、fast-tempo factor；
3. integer lag bounds 与 BPM support 的双重作用；
4. best-vs-alternative 的 `±2` lag exclusion；
5. five-candidate median filter；
6. endpoint geometric means；
7. `semi-Markov` 的 segmental 含义与非-generative caveat；
8. exact Direct count fallback；
9. downbeat meters 2--7、meter-change penalty、70-ms agreement、0.6 threshold；
10. first-5-s evaluation trim。

v5.1 已按代码恢复这些定义，同时保留 v5 的短句和问题驱动顺序。

---

## P1.5 Package / openness claim 目前过强

仓库当前状态不支持无条件写：

- `open-source`：若没有明确 license，公开可读不等于法律意义的 open-source；
- `pip-installable`：Git 安装与 PyPI release 不是同一件事；
- `madmom-compatible`：需要定义兼容层级并有接口测试。

在 release 完成前建议：

> We provide a reference Python implementation, a machine-readable frozen configuration, and an activation-level interface.

完成 license、PyPI、API test 后再升级措辞。

---

## P1.6 Literature/SOTA 表只能提供 context

表中系统使用不同：

- frontends / pretraining；
- checkpoints；
- dataset preprocessing；
- post-processors；
- evaluation / reporting protocol。

因此即使某个 CASM 数字最高，也不能单独支撑 decoder-level SOTA。decoder 机制主张只能来自 fixed-activation controlled comparison；literature table 只能写：

> provides system-level context

而不能替代同 backbone、同 activation、同 evaluator 的 paired comparison。

---

## 提交前的优先修复顺序

### 1. 冻结唯一主身份

建议统一为：

```text
Frozen-7F
candidate hash 93f40ad...
30--300 BPM
duration_sigma 0.15
first-5-s trim
piece-macro mir_eval
```

### 2. 重建 controlled post-processor table

先完成 BeatThis；再等 MSCNN/TCN cache/checkpoint refresh。不要让缺失 backbone 阻止正确报告一个已完成 panel，但不要用旧数值填空。

### 3. 同一 7F identity 重跑 ablations

优先级：

1. full CASM；
2. fixed precision / fixed target；
3. strength-only；
4. width-only；
5. one endpoint；
6. no count safeguard；
7. no downbeat agreement safeguard；
8. 55--215 support diagnostic。

所有 variants 必须使用同一 activations 和 evaluator。

### 4. 重生成 p0/p1

从同一 7F trace 生成 response law、edge distributions、representatives，并输出 manifest/hash 到图旁边。

### 5. 若要保留 calibration claim，重做 matched protocol

最小 matched design：

- 相同 calibration pieces；
- 相同 primary utility / tie break；
- 相同 fixed BPM support；
- 可比较的 search budget；
- rotating outer evaluation folds；
- protocol 在看 test 结果前冻结。

### 6. 最后再恢复 abstract 的数值结论

Abstract、Table 1、SOTA row、Conclusion 必须从同一个生成 artifact 自动同步，不再手工复制。

---

## Claim 审批矩阵

| Claim | 当前 verdict | 安全写法 |
|---|---|---|
| CASM is DP-based | 支持 | `a sparse candidate-event semi-Markov decoder solved by dynamic programming` |
| CASM uses local period | 支持 | 明确是 8-s local autocorrelation argmax lag |
| CASM models competitor ambiguity | 有条件支持 | `computes a best-versus-strongest-alternative margin`；不是 multi-hypothesis path |
| Low margin returns Direct | 不支持 | low margin weakens cost；count-ratio safeguard 才 return Direct |
| CASM has no tempo assumptions | 不支持 | one broad fixed support, no per-track BPM input |
| CASM has no learned weights | 支持 | 但必须同时承认 validation-selected global configuration |
| CASM is less calibration-sensitive than DBN | 当前不支持因果结论 | unmatched pipelines 下有 narrower descriptive spread |
| CASM improves every metric on 3 backbones | 当前 release 不支持 | 等 7F rows 重建后逐格验证 |
| SMC SOTA | 当前不可稳定主张 | literature context only；先统一 protocol/provenance |
| open-source / PyPI-ready | 取决于发布状态 | release 前用 `reference implementation` |

## v5.1 的定位

`casm_v5.1.tex` 是一份 **audit-safe revision**：

- 采用推荐 Methodology A；
- 修复术语、公式、fallback、tempo support 和 downbeat 描述；
- 删除旧配置机制图的渲染和悬空引用；
- 不展示 contaminated comparison / ablation tables；
- 只报告当前仓库可追溯的 Frozen-7F CASM scores；
- 在正文中明确哪些 refresh / matched experiments 尚未完成。

它不是“假装已经解决结果 provenance 的 camera-ready 稿”。等重跑完成后，可以把新的表和图无缝放回；在此之前，宁可留下清晰 limitation，也不要用语言润色掩盖 operating-point 冲突。
