# CASM tempo range 与论文 methodology 交叉审计

**日期：** 2026-09-22

**审计对象：** CASM decoder 实现、Frozen-7F tempo-range ablation、`casm_v3.0.tex` 与 `casm_v4.tex`

**目的：** 判断 CASM 是否需要 tempo range，并核对论文的方法描述、实验协议和结果主张是否与代码及归档证据一致

## 结论先行

### 最终判断

1. **现有 CASM 不能被描述为“不需要 tempo range”。** `min_bpm`/`max_bpm` 在代码中同时决定：
   - 局部 autocorrelation 搜索哪些周期；
   - dynamic program 允许连接哪些候选 beat。

   因而它们会改变局部目标周期、ambiguity margin、候选图的边，以及最终路径，并非仅用于显示或防止极端输出。

2. **没有理论理由必须使用 `[55,215]`。** 这一范围对 CASM 来说过窄，尤其会排除 SMC 中真实存在的慢拍解释。审计过的 Frozen-7F 实验中，`[30,300]` 相对 `[55,215]` 在 27 个 backbone × dataset/target × metric 汇总单元中有 **21 个更高、6 个更低**。

3. **当前最合理的默认值是 `[30,300]`，但应把它称为 broad fixed support，而不是精确的音乐 tempo prior。** 30 和 300 不是 CASM 理论推导出的唯一端点；它们是目前证据支持的、宽松的搜索/计算护栏。

4. **`[30,300]` 胜过 `[55,215]` 不等于“完全无约束会更好”。** 现有实验只有 `[30,300]`、`[55,215]` 和 `[30,215]`，没有移除候选边限制，也没有无界 local-period bank。因此论文目前没有证据支持 tempo-range-free 结论。

5. **如果论文现在必须冻结一个版本，我建议保留 `[30,300]`。** 写作上应强调 CASM 不需要 *per-track BPM input/tuning*，但仍使用一个跨曲目固定的宽 local-period/interval support。这个说法既符合代码，也保留了与 DBN 全局 tempo-state prior 的实质区别。

6. **`casm_v4.tex` 的 methodology 主公式总体与代码一致，但复现信息比 v3 少；结果表和若干结论则存在阻断级问题。** 最严重的是 v4 主表中 MSCNN/TCN 的 CASM 与 DBN 数字疑似错行，使正文的 “improves every metric” 目前无法由该表可靠支撑。建议先修结果来源与 operating-point 身份，再重新生成结论文字。

### 建议的论文一句话定位

> CASM does not require a track-specific BPM estimate or tempo trajectory prior, but uses a single broad, fixed local-period and transition support for all inputs.

这比 “CASM imposes no tempo assumptions” 更准确，也更容易经受审稿。

---

## 一、tempo range 在代码里到底做了什么？

### 1. 它首先限制 local-period hypothesis bank

与实验归档一致的原始 decoder 快照为：

```text
structbeat/decoders.py
SHA-256 f66e7dfb09b208882749fe6d212d8363b28b7a2da397b4ba297b93df1825eaed
```

当前仓库中的 release 实现 [`src/casm_beat_tracking/decoder.py`](../../src/casm_beat_tracking/decoder.py#L98) 保留了相同的 lag-bank、confidence、edge-gating 和 duration-cost 逻辑；release 默认配置 [`config/casm-7f-default.json`](../../config/casm-7f-default.json) 的 candidate hash 与 Frozen-7F archive 一致，并明确使用 30--300 BPM。因此下面的结论同时适用于实验快照与当前公开实现。

`local_period_score_matrix` 中的整数 lag 范围是

\[
\ell_{\min}=\max\!\left(2,\left\lceil\frac{60F}{b_{\max}}\right\rceil\right),
\qquad
\ell_{\max}=\min\!\left(T-1,\left\lfloor\frac{60F}{b_{\min}}\right\rfloor\right).
\]

每个 lag 的局部分数为

\[
q_i(\ell)=
\frac{\langle a_u a_{u-\ell}\rangle}
{\sqrt{\langle a_u^2\rangle\langle a_{u-\ell}^2\rangle+\epsilon_q}}
\left(\frac{\ell_{\min}}{\ell}\right)^\beta,
\]

其中窗口外和信号外使用 zero padding。代码再从这些 lag 中选择最佳周期，并将最佳分数与最佳 lag 附近 `±2` 帧以外的最强竞争者比较，得到 \(c_i\)。

因此，扩大范围并不只是“多允许几种最终 BPM”；它还会：

- 让原本被截掉的慢/快周期有机会成为 \(\tau_i\)；
- 引入新的 second-best hypothesis，从而可能降低 \(c_i\)；
- 避免在窄范围内因为竞争解释被人为删掉而得到虚高的 confidence。

这一点对 CASM 尤其重要，因为 \(c_i\) 会直接调节 duration cost。窄范围可能既选错 target，又对这个 target 过度自信。

### 2. 它还硬性限制 dynamic-programming edge

beat path 中一条边只有在帧间隔满足

\[
\left\lceil\frac{60F}{b_{\max}}\right\rceil
\le t_j-t_i \le
\left\lfloor\frac{60F}{b_{\min}}\right\rfloor
\]

时才会进入 duration-cost 比较。代码中的 `_decode_beats` 明确先用该区间筛 edge，再计算

\[
D_{ij}
=
\frac{\lambda c_{ij}}
{2[\sigma_0+(1-c_{ij})\sigma_u]^2}
\log^2\!\left(\frac{\Delta_{ij}}{\bar\tau_{ij}}\right).
\]

所以即使 \(c_{ij}\to0\) 令 soft duration cost 接近零，tempo range 仍然是 hard support。CASM 此时只是趋向 activation-dominated sparse-path decoding，并不会自动等同于 Direct；只有 event-count ratio 超出阈值时，显式 safeguard 才返回 Direct。

### 3. 50 Hz 下的实际离散范围

当前 activations 为 \(F=50\) Hz：

| 配置 | 允许帧间隔 | 允许秒数 | 由整数帧得到的有效边界 |
|---|---:|---:|---:|
| `[55,215]` | 14--54 帧 | 0.28--1.08 s | 约 55.56--214.29 BPM |
| `[30,215]` | 14--100 帧 | 0.28--2.00 s | 约 30--214.29 BPM |
| `[30,300]` | 10--100 帧 | 0.20--2.00 s | 30--300 BPM |

因此论文若写精确的连续区间，最好同时给出整数 lag 定义；`[55,215]` 在 50 Hz 下实际并不能精确表示两个端点。

### 4. 为什么不能简单把范围删掉？

当前实现没有一个等价于 “unbounded” 的安全参数值。直接去掉范围会带来四类变化：

1. **问题定义变了。** 最小 lag 在代码中还有 2 帧下限，相当于 50 Hz 下约 1500 BPM；最大 lag 若放到整首长度，则最低可表示 BPM 取决于曲目时长。所谓“无范围”会变成 track-length-dependent，而不是一个清晰的音乐模型。
2. **局部周期计算可能从有限 lag bank 膨胀到近似二次复杂度。** 当前实现为每个 lag 计算一条局部 correlation 序列，并存储 `number_of_lags × number_of_candidates` 的矩阵。
3. **候选图会接近 all-pairs。** 去掉最大 edge interval 后，动态规划的前驱搜索最坏可回到 \(O(N^2)\)。
4. **存在退化风险。** 当 \(c\approx0\) 时 duration cost 消失；若同时没有最小 edge interval，DP 可以连接非常密集的正分数候选，随后频繁触发 count-ratio fallback。此时方法可能实质退回 Direct，却付出更高计算代价。

所以，“不需要窄的音乐 tempo prior”是合理假设；“不需要任何 period/edge support”则是一个尚未实现、尚未验证的新方法版本。

---

## 二、实验实际上支持什么？

### 1. 证据完整性

本次核对使用 Frozen-7F tempo-range archive。该归档包含：

- 3 个 backbone；
- GTZAN 的 3 个 full-data checkpoints，每个 993 首；
- SMC 的 8 个 backbone-OOF folds，共 217 首；
- `[30,300]`、`[55,215]`、`[30,215]` 三个条件；
- piece-level 输出、聚合脚本、本地 QA 与 Gadi 独立重聚合。

归档总校验清单全部通过；Gadi 从 piece-level 独立重聚合也为 `PASS`，最大 aggregate absolute error 为约 \(1.42\times10^{-14}\)。三种范围仅改变 `min_bpm` 和 `max_bpm`。

Frozen-7F 配置 hash：

```text
93f40ad87602ae68d84c6d1d72e307c27a67cc94d2b508f619f3376df08ae7de
```

该 hash 也已写入仓库的 [`casm-7f-default.json`](../../config/casm-7f-default.json)。

必须保留的限制是：7F decoder configuration 使用 SMC folds 1--7 选择，因此 8-fold SMC 汇总虽然对 backbone training 是 OOF，但只有 fold 0 对 decoder calibration 真正 held out。

### 2. `[30,300] - [55,215]` 的实际差值

下表为 percentage-point 差值；正数表示宽范围更好。

| Backbone | Panel / target | F1 | CMLt | AMLt |
|---|---|---:|---:|---:|
| BeatThis | GTZAN beat | -0.05 | -0.11 | -0.04 |
| BeatThis | GTZAN downbeat | +0.10 | +0.15 | +0.15 |
| BeatThis | SMC beat | **+0.86** | **+1.93** | +0.54 |
| MSCNN | GTZAN beat | -0.04 | -0.22 | +0.06 |
| MSCNN | GTZAN downbeat | +0.25 | +0.44 | +0.49 |
| MSCNN | SMC beat | **+0.66** | **+1.08** | +0.28 |
| TCN | GTZAN beat | +0.05 | +0.00 | +0.02 |
| TCN | GTZAN downbeat | +0.17 | +0.17 | +0.46 |
| TCN | SMC beat | **+0.86** | **+2.02** | **-0.63** |

准确解读是：

- `[30,300]` 在 27 个汇总单元中赢 21 个，优势主要集中于 SMC F1/CMLt 和 GTZAN downbeat；
- 它不是逐项支配：例如 TCN/SMC AMLt 下降 0.63 pp，BeatThis/MSCNN 的部分 GTZAN beat 指标略低；
- 因而 `[30,300]` 是更稳健的跨数据集默认 support，而不是保证每个指标都最大的 oracle setting。

### 3. range 并非“几乎从未生效”

piece-level 比较 `[30,300]` 与 `[55,215]`：

| Backbone | Panel | 至少一个 beat metric 改变的曲目比例 | beat count 改变比例 |
|---|---|---:|---:|
| BeatThis | SMC | 56.2% | 55.3% |
| MSCNN | SMC | 71.9% | 68.2% |
| TCN | SMC | 70.0% | 64.5% |
| BeatThis | GTZAN × 3 checkpoints | 10.8% | 11.5% |
| MSCNN | GTZAN × 3 checkpoints | 19.6% | 18.4% |
| TCN | GTZAN × 3 checkpoints | 14.3% | 13.7% |

这说明范围在大量 SMC 曲目上真实改变了路径，不是 inactive hyperparameter。

### 4. `[30,215]` 帮助区分上下界的作用

`[30,215]` 与 `[55,215]` 的差异只放宽 lower-BPM boundary；它已经复现了大部分 SMC 改善。再从 `[30,215]` 放宽到 `[30,300]`，SMC 变化大多很小，而 GTZAN downbeat 更一致地受益。

因此目前最可信的机制解释是：

- SMC 的主要问题是 55 BPM lower bound 过高；
- 300 BPM upper bound 对 SMC beat 不是主要驱动，但为快速/细分解释和 GTZAN downbeat 提供了额外空间；
- 这支持 broad support，而不是支持 unbounded decoding。

### 5. 可以和不可以写进论文的结论

**可以写：**

> Widening the fixed support from 55--215 to 30--300 BPM improves 21 of 27 aggregate metric cells, with the clearest gains on low-tempo SMC material. The support nevertheless remains a fixed computational and hypothesis boundary, not a per-track tempo input.

**不可以据现有实验写：**

- CASM 不需要 tempo range；
- CASM 对 tempo support 完全不敏感；
- `[30,300]` 在所有指标上都优于 `[55,215]`；
- 30 和 300 是理论最优边界；
- CASM 完全没有 tempo assumption。

---

## 三、`casm_v3.0.tex` 与 `casm_v4.tex` methodology 核对

### 总体评价

v4 的组织和直觉解释比 v3 更紧凑，核心 path objective、ambiguity margin 和 duration cost 与代码相符。问题在于，v4 为压缩篇幅删掉了若干决定可复现性和论证边界的细节，同时实验/结果段落混入了与审计数据不一致的数字和过强结论。

最好的版本不是回退到 v3，而是：**保留 v4 的结构，恢复 v3 的精确定义与 caveat，并用唯一一个已锁定 operating point 重新生成全部表格。**

### v3 中应恢复到 v4 的内容

1. `casm_v3.0.tex` 的 local autocorrelation 公式给出了 normalization、zero padding 和 fast-tempo bias；v4 只说 “normalized autocorrelation”，导致 \(q_i(\ell)\)、admissible lag、窗口和 bias 不足以复现。
2. v3 明确写了 CASM 的 “semi-Markov” 含义，并声明它不是 generative HSMM、segment potentials 也不是 learned；这一 caveat 对命名防御很重要。
3. v3 的 evaluation 段包含 first-5-s trim；v4 漏掉了，而归档协议确实使用 `trim_seconds=5.0`。
4. v3 的主表 caption 明确区分 Direct absolute scores 与其他行相对 Direct 的 percentage-point changes；v4 caption 删除了这一关键信息。

### v4 中正确且应保留的内容

1. ordered candidate path 与 complete candidate-to-candidate duration 的定义；
2. top-vs-alternative period-separation margin，并明确 \(c_i\) 不是 calibrated probability；
3. endpoint geometric mean：\(\bar\tau_{ij}=\sqrt{\tau_i\tau_j}\)、\(c_{ij}=\sqrt{c_ic_j}\)；
4. restart after an unfavourable prefix；
5. count-ratio safeguard 与 beat-synchronous downbeat decoding；
6. “fixed global parameters, input-conditioned operating point” 这一核心定位。

---

## 四、必须修改或确认的具体问题

### P0：提交前阻断项

#### P0.1 主结果表出现疑似 CASM/DBN 整行错配

位置：[`casm_v4.tex` 主结果表](../main/casm_v4.tex#L334)

当前表中：

- MSCNN CASM 的 SMC `+0.3/+3.5/+6.8` 与审计过的 Frozen-7F full table 中 **DBN SMC-opt** 行完全一致；
- MSCNN DBN 30--300 的 `-0.2/+2.2/+4.1` 与审计表中的 **CASM [7F]** 行完全一致；
- TCN CASM 的 `+1.7/+4.5/+8.2` 与审计表中的 **DBN SMC-opt** 行完全一致；
- TCN DBN 30--300 的 `-0.4/+2.1/+5.9` 与审计表中的 **CASM [7F]** 行完全一致。

这不是舍入误差，极像 row assignment 被交换。BeatThis 的 55--215 SMC F1 在当前 v4 为 `+0.1`，审计过的 Frozen-7F 表则为 `-0.6`。当前 30--300 CASM 行也无法作为 Frozen-7F tempo archive 的直接重现。

**建议：不要逐格手改。** 从锁定的 piece-level 结果重新生成完整表，并在生成阶段验证 method label、config hash、range 和 aggregation source。之后再同步 SOTA table、abstract 和正文。

#### P0.2 “30--300 improves every metric” 必须在重建表后重新验证

位置：[`casm_v4.tex` 结果解释](../main/casm_v4.tex#L470)

该句当前声称 CASM 在所有 backbone、dataset、F1/CMLt/AMLt 上都改善 Direct，但紧邻的 30--300 CASM 行存在 P0.1 的 method-label/row-source 问题，因而这项 universal claim 不能由当前表验证。

Frozen-7F tempo archive 的 30--300 absolute scores 与 v4 中显示到一位小数的 Direct baselines 粗略比较时，所有单元确实都更高；但严谨的 percentage-point claim 必须使用同一 evaluator、checkpoint aggregation 和未舍入的 Direct artifact 重算。另一方面，55--215 的 Frozen-7F CASM 在 BeatThis/MSCNN/TCN 的 SMC F1 上为负，说明该结论严格依赖 30--300 operating point，不能泛化成 “CASM always improves every metric”。

**建议：** 重建表后若未舍入差值仍全部为正，可保留限定式 “with the frozen 30--300 configuration”；否则改为 “generally preserves F1 while improving several continuity metrics”。

#### P0.3 4F/7F operating point 身份混杂

位置：[`casm_v4.tex` calibration](../main/casm_v4.tex#L325)、主表与 SOTA 表

v4 声称所有主表使用 7F，但当前表值、现有 mechanism protocol 和历史归档中同时出现 4F 与 7F 配置。两者不能共用一个 `CASM` 标签。

**必须二选一并全篇统一：**

- 若采用 7F：用 Frozen-7F hash 和 7F piece-level archive 重建所有 CASM 数字；明确 SMC folds 1--7 参与 decoder selection，因此整体 SMC 不是 nested decoder estimate。
- 若采用 4F：必须如实标为 post-hoc/exploratory operating point，并说明 folds `{2,7,1,3}`，不能继续称为 “maximally supported 7F”。

从可辩护性看，我更建议 7F 作为 confirmatory main configuration，4F 仅留在 sensitivity/supplementary。

#### P0.4 GTZAN checkpoint/aggregation 存在三套互相冲突的 provenance

位置：[`casm_v4.tex` evaluation](../main/casm_v4.tex#L318)

目前同时存在三种说法：

1. v4 写的是 8 个 fold-specific checkpoints 都在 GTZAN 上评价；
2. 本次审计的 Frozen-7F tempo archive 包含 3 个 full-data checkpoints `final0/final1/final2`，每个条件均有 piece-level 文件、SHA 和独立重聚合；
3. 新增的 [`docs/RESULTS.md`](../../docs/RESULTS.md#gtzan-status) 又写明目前只保留一个 post-hoc-selected `final1` 点，publishable 的 Frozen-7F `final0/final1/final2` refresh 仍 pending。

这三者不能同时作为同一主表的 provenance。可能的解释是 release 文档和 tempo-range archive 指向不同 activation/checkpoint inventory，但在给出 manifest-level 对应关系前不能假定它们相同。需要逐项确认 checkpoint checksum、activation source、decoder hash、trim/evaluator 和 aggregation script，再选择唯一 publishable source；随后同步 protocol sentence、表格 caption、piece count、checkpoint count 和不确定性定义。

### P1：方法可信度和复现性问题

#### P1.1 v4 缺少 \(q_i(\ell)\) 的完整定义

位置：[`casm_v4.tex` local period 段](../main/casm_v4.tex#L225)

应恢复 v3 的公式，并明确：

- \(\ell_{\min},\ell_{\max}\) 的整数 rounding；
- 8 s centered window；
- zero padding；
- fast-tempo factor \((\ell_{\min}/\ell)^\beta\)；
- 最佳/替代 lag 的 `±2` frame exclusion；
- 五候选 median filter。

否则读者无法从论文复现 \(\tau_i\) 与 \(c_i\)，而 tempo-range 的真实作用也被隐藏。

#### P1.2 candidate evidence \(e_i\) 没有定义

位置：[`casm_v4.tex` candidate path](../main/casm_v4.tex#L197)

代码实际使用

\[
e_i=\operatorname{clip}\!\left(z^{\mathrm b}_{t_i}/T,-L,L\right),
\]

而不是泛指 activation score。应给出该式，并区分 candidate selection 用 sigmoid activation、node evidence 用 scaled/clipped logit。

#### P1.3 必须把 tempo support 的两个角色写清楚

位置：[`casm_v4.tex` lines 203--204](../main/casm_v4.tex#L203)

当前只写 edge admissibility，没有说明同一个范围还定义 autocorrelation lag bank。建议明确称为：

> a shared broad support for local-period hypotheses and candidate-to-candidate transitions

长远看最好在代码中拆成 `period_min/max_bpm` 与 `edge_min/max_bpm`；即使最终数值相同，论文也能清楚区分 soft target estimation 与 hard graph support。

#### P1.4 “defer to Direct” 需要更精确

位置：abstract/introduction/figure caption 与 methodology

当 \(c\to0\) 时只是 duration penalty 变弱；CASM 仍使用自己的 candidate threshold、candidate graph 和 tempo-support edges。只有 count-ratio safeguard 触发时才精确返回 Direct。

建议改成：

> relaxes toward activation-dominated sparse-path decoding; the exact Direct path is returned only by the explicit count-ratio safeguard.

如果某个案例确实触发了 safeguard，figure caption 可以单独说该案例返回 Direct，但不能把它推广成一般数学性质。

#### P1.5 恢复 5 s evaluation trim

位置：[`casm_v4.tex` evaluation](../main/casm_v4.tex#L318)

v3 和实验归档均使用 first 5 s ignored。v4 必须恢复，否则 protocol 与结果不一致。

#### P1.6 baseline wrapper 描述过于简略

位置：[`casm_v4.tex` post-processors](../main/casm_v4.tex#L320)

“released/default parameters” 不足以覆盖实际 wrapper 行为。至少在正文、supplement 或 code reference 中说明：

- PLPDP 的 50→100 fps resampling、beat/downbeat activation 组合、异常时 Direct fallback，以及 downbeat peak/snap；
- CRF/CombFilter 的 beat/downbeat stream 处理与 snap；
- DBN 的 joint activation construction；
- 哪些方法使用 30--300，哪些使用 released default，以及 SMC-opt 标签究竟表示什么。

#### P1.7 缺少完整 frozen configuration 身份

方法段应至少给出 compact parameter table 或指向可审计的 supplement/config：candidate threshold、window、tempo bias、temperature、logit clip、duration weight、\(\sigma_0\)、\(\sigma_u\)、fallback ratios、meters、meter-change penalty、downbeat agreement threshold/tolerance，以及 operating-point hash。当前 [`casm-7f-default.json`](../../config/casm-7f-default.json) 已提供合适的机器可读入口，论文和表格应引用同一 hash。

这不是要求正文塞入所有工程细节，而是避免 “CASM” 在不同表中指向不同配置。

#### P1.8 calibration sensitivity 的强结论目前不能成立

位置：abstract、[`casm_v4.tex` introduction](../main/casm_v4.tex#L105)、[`casm_v4.tex` sensitivity interpretation](../main/casm_v4.tex#L568)

现有 CASM 与 DBN sensitivity experiment 的 calibration population、sample size、selection objective 和 search space 不匹配。CASM 1F 使用约 562--575 首、多 corpus；DBN 1F 仅使用 27--28 首 SMC。CASM fixed support，DBN search 又允许 tempo support 变化。当前结果只能作为各自协议下的 descriptive audit，不能推出 model-class 层面的 “CASM is intrinsically less sensitive than DBN” 或 DBN over-specialisation。

另外 “CASM central performance improves consistently ... on both panels” 也不严格成立，例如 downbeat AMLt 的 4F mean 略高于 7F。详细证据见现有审计：[calibration-scale scientific audit](2026-09-05_calibration_scale_scientific_audit.md)。

建议在公平重跑前删除 abstract 中该强主张，将正文改为：

> Under their respective calibration procedures, CASM exhibited a narrower descriptive spread; because the calibration inventories and searches were unmatched, this comparison does not isolate decoder-class sensitivity.

### P2：建议修正但不改变核心方法的问题

#### P2.1 恢复 semi-Markov 命名 caveat

v3 的表述更稳：CASM 的 transition 消耗 variable-length candidate segment 并整体评分 duration；它不是 generative HSMM，也不是 learned semi-CRF。建议在 v4 加回一句。

#### P2.2 不要暗示 CASM “tempo-free”

“no externally supplied/per-track BPM” 是真的；“no tempo assumption” 不是真的。Abstract、Introduction 和 Conclusion 应始终区分：

- DBN：固定全局 tempo-state support/transition law，并推断 tempo-phase path；
- CASM：固定宽 local hypothesis/edge support，但 local target 与 stiffness 由 activation context 决定。

#### P2.3 grammar 与 LaTeX 清理

- `resulting in overrides correct local evidence` 应改为 `causing them to override correct local evidence`；
- `As we defined our task is offline...` 需要整句重写；
- `many SMC data are fall below 55 BPM` 应改为 `many SMC excerpts fall below 55 BPM`；
- `with all other CASM settings remain unchanged` 应为 `with all other CASM settings remaining unchanged`；
- `pick-peaking` 应为 `peak-picking`；
- preamble 同时加载 `\usepackage{xcolor}` 与 `\usepackage[table]{xcolor}`，存在 option-clash 风险，只保留后者；
- 当前 `\showchangestrue` 会把 `\rev{}` 内容渲染成红色，正式提交前应切换为 false 或移除 revision wrapper。

---

## 五、建议直接替换/补入的英文方法文字

### 1. tempo support 定位

> CASM uses one broad fixed support for both local-period hypotheses and candidate-to-candidate transitions. At frame rate \(F\), the admissible integer lags are \(\ell\in[\max(2,\lceil60F/b_{\max}\rceil),\min(T-1,\lfloor60F/b_{\min}\rfloor)]\). We use \(b_{\min}=30\) and \(b_{\max}=300\) BPM for every track and backbone. This support bounds the hypothesis bank and computation; it is not a track-specific BPM estimate or a globally tracked tempo trajectory.

### 2. ambiguity relaxation 的精确表述

> As \(c_{ij}\) decreases, the duration cost weakens and CASM approaches activation-dominated sparse-path decoding, although the candidate graph remains bounded by the fixed transition support. The exact Direct path is returned only when the explicit event-count safeguard is triggered.

### 3. tempo-range ablation 的安全结果表述

> Widening the support from 55--215 to 30--300 BPM improved 21 of 27 aggregate metric cells. The clearest gains occurred on SMC F1 and CMLt, consistent with the narrower range excluding slow-beat interpretations; a 30--215 condition recovered most of this SMC gain. The wider range was not uniformly better for every metric, so we interpret 30--300 BPM as a more robust shared support rather than an oracle per-dataset setting.

### 4. semi-Markov caveat

> We use “semi-Markov” in the segmental decoding sense: each transition consumes and scores a variable-duration candidate-to-candidate interval. CASM is neither a generative hidden semi-Markov model nor a learned semi-CRF.

---

## 六、真正回答“能否取消 tempo range”的最小下一步实验

当前三档 ablation 只能比较边界，不能识别 range 的两个功能。建议将代码参数拆开，做一个 \(2\times2\) factorial：

| Local-period bank | DP edge gate | 回答的问题 |
|---|---|---|
| 30--300 | 30--300 | 当前 control |
| 30--300 | broad/no hard gate | hard edge gate 是否必要 |
| wider bank | 30--300 | period-search boundary 是否限制 target/confidence |
| wider bank | broad/no hard gate | 两者同时放宽的相互作用 |

这里的 “wider” 仍应先用有限且可复现的范围，例如 `[20,400]`、`[15,600]`，而不是直接使用曲目长度定义的无界 lag。每个条件除 F1/CMLt/AMLt 外应报告：

- local-period argmax 落在上下 boundary 的比例；
- selected edges 接近 boundary 的比例；
- \(c_i\) 分布和最强 alternative 的变化；
- count-ratio fallback rate；
- selected/direct count ratio；
- runtime、peak memory、candidate edge 数。

若 “no hard gate” 与 `[30,300]` 性能相同且几乎没有 boundary-active edges，才能说 edge range 在当前数据上可能冗余。若 wider bank 改变 \(c_i\) 而 improves performance，则应重构 local-period estimation，而不是简单声称整个方法不需要 range。

---

## 七、最终论文决策建议

1. **方法默认值：** 采用 `[30,300]`，表述为 broad shared support。
2. **理论主张：** 不说 tempo-free；说 no per-track BPM input/tuning，且 local duration potential 是 input-conditioned。
3. **ablation：** 主文至少保留 `[55,215]` vs `[30,300]`；若空间允许加入 `[30,215]`，它对 lower-bound 机制解释很关键。
4. **operating point：** 建议统一 Frozen-7F，并用其 hash/locked archive 重建所有表；4F 仅作 exploratory sensitivity。
5. **结果写作：** 用 “21/27 aggregate cells” 和具体例外，避免 universal-improvement claim。
6. **当前最紧急动作：** 在任何投稿版本生成前，先修复/重建 v4 主结果表与 SOTA 表，确认 CASM/DBN row label、4F/7F、checkpoint aggregation，并解决 tempo-range archive 与 `docs/RESULTS.md` 的 GTZAN provenance 冲突。
7. **methodology 合并策略：** 保留 v4 结构，恢复 v3 的 \(q_i(\ell)\)、lag bounds、zero padding、5 s trim 和 semi-Markov caveat，再补 \(e_i\) 与 frozen-config provenance。

## 审计置信度

- **代码结论：高。** tempo range 的两处作用可直接从与归档 hash 匹配的 decoder 快照确认。
- **`[30,300]` 优于 `[55,215]` 的 archive-internal 结论：高。** piece-level 数据、本地聚合、独立 Gadi 聚合和 SHA 清单一致。
- **将该 archive 直接用作论文最终 GTZAN 主表的置信度：中等。** 当前 release 文档对可用 checkpoint inventory 有冲突陈述，必须先完成 manifest-level provenance reconciliation。
- **对未见数据的普遍化：中等。** 数据集仍主要是 GTZAN/SMC，且 7F decoder selection 对 SMC 不是完全 nested。
- **“完全取消范围”的效果：未知。** 该条件尚未实现或实验，不能由现有三档 range ablation 外推。
