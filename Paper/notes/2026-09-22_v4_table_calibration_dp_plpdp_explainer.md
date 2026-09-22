# CASM v4 表格错配、calibration protocol、DP 与 PLPDP：逐项解释

**日期：** 2026-09-22

**范围：** `Paper/main/casm_v4.tex`、`Paper/main/casm_v3.0.tex`、当前 release decoder、Frozen-7F tempo-range archive、PLPDP 论文翻译与实验 wrapper

**前置审计：** [CASM tempo range 与 methodology 交叉审计](2026-09-22_casm_tempo_range_and_methodology_audit.md)

## 先给最直接的答案

1. 上一份报告中的“MSCNN/TCN CASM 与 DBN 数字疑似整行错配”说得太粗。更精确的结论是：
   - **SMC 的三个指标块发生了可以逐值确认的 CASM↔DBN 交叉贴错；**
   - 同一行的 GTZAN 数字又来自另一方法配置或另一 operating point；
   - 所以几行最终成了由不同来源拼接的 **Frankenstein rows**，不能代表任何一次完整实验。

2. 这里不是“结果不好所以怀疑错”，而是出现了**数值身份冲突**：v4 中标作 CASM 的三个 SMC 数字，与归档里 DBN 的三个数字逐位完全相同；标作 DBN 的三个数字，又与归档里 CASM 的三个数字逐位完全相同。四组三元组在 MSCNN 和 TCN 上都发生同样的交换，不能解释成舍入误差或随机波动。

3. v4 并不是这次错配的起点。Git 历史显示，v4 在 commit `882f981b` 中建立时已经带着这些数字；该 commit 之前的 `casm_v3.tex` 也已有同样的混合行。**因此应该说 v4 继承了旧表污染，而不是说 v4 作者在该 commit 中新制造了错误。**

4. `calibration protocol 不匹配` 的意思是：CASM 与 DBN 的配置选择实验用了不同数量/构成的曲目、不同优化目标和不同搜索自由度。两图可以分别正确，但不能把方差差异直接归因于“CASM 的模型结构更稳定”。

5. **CASM 仍然明确是 DP-based。** DP 是 dynamic programming（动态规划），不是 deep learning。CASM 的 beat path 和 downbeat path 都由动态规划求解。

6. **PLPDP 也同样是 DP-based，而且它与 CASM 的高层数学骨架很接近。** CASM 的实质差异不在“第一次把局部周期放进 DP”，而在：
   - 只在 activation 局部极大值构成的稀疏候选图上搜索；
   - 用候选位置的局部归一化 autocorrelation 估计周期；
   - 用“最佳周期与最强竞争周期的相对间隔”定义 ambiguity margin；
   - 用边两端的周期与置信度对称地构造 duration potential；
   - 再加 count-ratio fallback 和 beat-synchronous downbeat DP。

7. 如果“回复 v3 的共识”指的是“恢复 v3 的公式”，我的建议不是回退整个 v3，而是：
   - **恢复 v3 的 local-autocorrelation 明确定义和 semi-Markov caveat；**
   - 保留 v4 更紧凑的章节结构；
   - 不恢复 v3 的结果表，因为当前 v3 表本身也含有相同的错配。

---

## 一、v4 主表到底发生了什么？

### 1. 表的数字语义

在 [`casm_v4.tex` 的主表](../main/casm_v4.tex#L334) 中：

- Direct 行是绝对分数；
- 其余行是相对同一 backbone Direct 的 percentage-point change；
- 每个方法行共有九个变化量：
  - GTZAN Beat：F1 / CMLt / AMLt；
  - GTZAN Downbeat：F1 / CMLt / AMLt；
  - SMC Beat：F1 / CMLt / AMLt。

v4 caption 没有把“Direct 是绝对值，其余为 delta”写出来，这本身就是一个需要修复的可读性问题。

### 2. 最硬的证据：SMC 三元组被成块交换

以下“归档身份”来自已通过 checksum、本地 QA 和 Gadi 独立重聚合的 Frozen-7F full table。

| Backbone | v4 行标签 | v4 的 SMC 三元组 | 归档中这组三元组真正属于 |
|---|---|---:|---|
| MSCNN | CASM, 30--300 | `+0.3 / +3.5 / +6.8` | **DBN, 30--300** |
| MSCNN | DBN, 30--300 | `-0.2 / +2.2 / +4.1` | **CASM [7F], 55--215** |
| TCN | CASM, 30--300 | `+1.7 / +4.5 / +8.2` | **DBN, 30--300** |
| TCN | DBN, 30--300 | `-0.4 / +2.1 / +5.9` | **CASM [7F], 55--215** |

因此它不是“看上去有点不合理”，而是有以下精确关系：

\[
\begin{aligned}
\text{v4 MSCNN/CASM/SMC}
&=
\text{archive MSCNN/DBN-wide/SMC},\\
\text{v4 MSCNN/DBN-wide/SMC}
&=
\text{archive MSCNN/CASM-narrow/SMC},\\
\text{v4 TCN/CASM/SMC}
&=
\text{archive TCN/DBN-wide/SMC},\\
\text{v4 TCN/DBN-wide/SMC}
&=
\text{archive TCN/CASM-narrow/SMC}.
\end{aligned}
\]

每项都是四舍五入后一位小数的**完整三格一致**。MSCNN 和 TCN 都重复相同交换模式，故“偶然相同”基本可以排除。

### 3. 为什么不能简单说“整行互换”？

因为每行只有 SMC block 明确交换，GTZAN block 没有一起交换。

#### TCN 是最清楚的 Frankenstein row

v4 的 TCN CASM 30--300 行：

| 区块 | v4 数字 | 可验证身份 |
|---|---:|---|
| GTZAN Beat | `+0.3 / +1.3 / +1.6` | CASM [7F] **55--215** |
| GTZAN Downbeat | `+2.1 / +9.2 / +13.4` | CASM [7F] **55--215** |
| SMC Beat | `+1.7 / +4.5 / +8.2` | **DBN 30--300** |
| v4 行标签 | CASM, 30--300 | 与上述两个来源都不一致 |

这条行并不对应：

- CASM 30--300；
- CASM 55--215；
- DBN 30--300；
- 或任何已验证的一次完整 aggregate。

它是“CASM narrow 的 GTZAN 六格 + DBN wide 的 SMC 三格”，但标签写成 CASM wide。

TCN DBN 30--300 行则是：

| 区块 | v4 数字 | 可验证身份 |
|---|---:|---|
| GTZAN Beat | `-1.9 / -0.8 / +4.4` | DBN 30--300 |
| GTZAN Downbeat | `-0.2 / +8.9 / +9.3` | DBN 30--300 |
| SMC Beat | `-0.4 / +2.1 / +5.9` | CASM [7F] 55--215 |

所以这行是“DBN wide 的 GTZAN 六格 + CASM narrow 的 SMC 三格”。

#### MSCNN 的情况更混

v4 的 MSCNN CASM 30--300 行：

| 区块 | v4 数字 | 与 Frozen-7F 归档的关系 |
|---|---:|---|
| GTZAN Beat | `+0.4 / +1.6 / +2.4` | 与 CASM 55--215 相同 |
| GTZAN Downbeat | `+1.5 / +12.5 / +18.3` | 不等于已验证的 CASM 55--215，也不等于 tempo-range archive 的 30--300 |
| SMC Beat | `+0.3 / +3.5 / +6.8` | 等于 DBN 30--300 |

v4 的 MSCNN DBN 30--300 行：

| 区块 | v4 数字 | 可验证身份 |
|---|---:|---|
| GTZAN Beat | `-1.1 / +0.2 / +5.9` | DBN 30--300 |
| GTZAN Downbeat | `-0.9 / +9.5 / +14.6` | DBN 30--300 |
| SMC Beat | `-0.2 / +2.2 / +4.1` | CASM [7F] 55--215 |

因此上一份报告的“整行错配”应改写为：

> MSCNN/TCN 的 SMC 三指标块发生精确的 CASM↔DBN provenance exchange；部分 GTZAN 块同时来自不同 CASM range/operating point，最终形成方法和配置身份不一致的混合行。

### 4. BeatThis 区块也不是一个干净的 Frozen-7F 重现

v4 的 BeatThis CASM 30--300 与验证过的 Frozen-7F 30--300 对比如下：

| Panel | v4 | Frozen-7F 30--300 |
|---|---:|---:|
| GTZAN Beat | `+0.3 / +0.8 / +1.2` | `0.0 / +0.4 / +0.6` |
| GTZAN Downbeat | `+0.7 / +3.6 / +8.0` | `+0.6 / +3.1 / +6.0` |
| SMC Beat | `+0.3 / +2.4 / +3.6` | `+0.2 / +2.4 / +2.6` |

这说明 v4 的 BeatThis wide row 至少不是当前锁定的 Frozen-7F wide result。

v4 的 BeatThis 55--215 行大部分与 Frozen-7F narrow row 相同，但 SMC F1 写成 `+0.1`，验证归档为 `-0.6`。因此即使在看似正确的 narrow row 中，也有单元来源不一致。

### 5. 所以 v4“错”在哪里？

严格说有四层问题：

#### A. 数值 provenance 错

同一个数值 block 被放到了错误的方法标签下。SMC block 的交换已能逐值证明。

#### B. configuration identity 错

标为 30--300 的 CASM 行里出现了已验证为 55--215 的 block。即使方法标签仍是 CASM，range 身份也不对。

#### C. operating point 混用

BeatThis wide 行与 Frozen-7F wide 结果不符，说明它可能来自旧 4F、旧 decoder、旧 checkpoint aggregation 或另一轮未锁定结果。当前 Git 表格没有携带每个 block 的 config hash/aggregation manifest，无法再仅凭数字确定其唯一来源。

#### D. 表注不足

caption 没说明哪些是 absolute score、哪些是 delta，也没绑定 config hash、aggregation protocol 和 checkpoint policy。这使手工复制时很难被自动发现。

### 6. Git 历史能证明什么，不能证明什么？

能够证明：

- [`casm_v4.tex`](../main/casm_v4.tex#L334) 的整张表在 commit [`882f981b`](https://github.com/zhanh-he/casm-beat-tracking/commit/882f981b8612c3e50d4795864ad6fb2672aeb7e4) 中进入当前路径；
- `git blame` 将表格第 334--470 行全部指向该 commit；
- 该 commit 的父版本 `Paper/0904_1335_overleaf/casm_v3.tex` 已经包含同样的 MSCNN/TCN 混合值；
- 当前 [`casm_v3.0.tex`](../main/casm_v3.0.tex#L377) 也保留了这些值。

不能证明：

- 最初是手工 copy/paste 错；
- 是生成脚本 row key 错；
- 是后处理表格时 label 错；
- 还是旧实验文件本身命名错。

Git 里没有“一格数字 → 原始 aggregate 文件 → config hash”的生成记录，故具体人为/脚本原因只能推测。最稳妥的措辞是：

> The table contains a demonstrable provenance/assignment error, but the repository history does not identify the original causal action.

### 7. 为什么不能只把 CASM 和 DBN 的 SMC 三格换回来？

因为：

- CASM 行的 GTZAN block 仍可能是 55--215，却标作 30--300；
- MSCNN CASM downbeat block 仍无已验证来源；
- BeatThis wide row 仍不是 Frozen-7F wide；
- caption 和正文的 universal claim 仍依赖混合 operating points；
- 手工换格会继续保留没有 manifest 的表。

正确修法是：

1. 决定唯一主 operating point，例如 Frozen-7F + 30--300；
2. 从 piece-level outputs 重聚合；
3. 用脚本一次性生成整表；
4. 每行写入 method、range、config hash、backbone/checkpoint aggregation policy；
5. 自动检查：
   - Direct absolute 与 delta 的关系；
   - 行标签与 config metadata；
   - 重复三元组是否跨方法异常复用；
   - 表中数值能否从 unrounded aggregate 重新得到；
6. 再重写表后正文，而不是让正文迁就旧表。

---

## 二、“calibration protocol 不匹配”到底是什么意思？

### 1. 这里的 calibration 不是训练 neural network

CASM decoder 没有用反向传播训练的 weights，但它有一组全局 scalar configuration。给定 calibration data \(D_S\)、候选配置集合 \(\Theta\) 和选择效用 \(U\)，过程可以写成：

\[
\hat\theta_S
=
\arg\max_{\theta\in\Theta} U(D_S;\theta).
\]

选好后，在测试曲目 \(x\) 上冻结参数，再做结构化推断：

\[
\hat y_x
=
\arg\max_y E(y;a_x,\hat\theta_S).
\]

第一式是 supervised validation-based configuration selection，第二式才是固定参数下的 DP inference。

因此：

- CASM 没有训练 decoder weights；
- 但它不是 parameter-free；
- 它用标注 development data 做过一次全局 calibration；
- 测试时没有 per-track labelled tuning。

### 2. “protocol”包含什么？

一个 calibration protocol 不只是“用了几个 fold”，而至少包括：

1. calibration 曲目来自哪里、共有多少首；
2. 哪些指标进入 selection objective；
3. 哪些参数允许搜索；
4. candidate grid/search budget；
5. tie-break 和 guard；
6. 是否固定 tempo support；
7. 最后在哪个 held-out panel 上评价。

只要这些关键部分不同，比较的就是两个**完整 selection pipelines**，而不是只比较 CASM 和 DBN 的 decoder 结构。

### 3. 当前 CASM 与 DBN 的具体不匹配

#### A. calibration population 与样本量不匹配

| Scale | CASM calibration inventory | 其中 SMC | DBN calibration inventory |
|---|---:|---:|---:|
| 1F | 562--575 首，多数据集 | 27--28 | 27--28 首，SMC only |
| 2F | 1129--1148 首，多数据集 | 54--55 | 54--55 首，SMC only |
| 4F | 2267--2287 首，多数据集 | 108--109 | 108--109 首，SMC only |
| 7F | 3985 首，多数据集 | 190 | 190 首，SMC only |

因此同样叫“1F”时，CASM 约有 570 首、跨多个 corpus，DBN 只有约 27 首 SMC。CASM 的选择结果更稳定，可能只是因为看过的 calibration sample 多约二十倍且更多样，而不能自动归因于 CASM 的数学结构。

这也暴露了 v4 第 326 行的文字问题。当前写的是 “calibrated once on the union of SMC folds 1--7”，容易让人理解为只用了 190 首 SMC；实际 CASM staged inventory 是按 BeatThis fold 过滤、没有按 dataset 过滤，7F 共 3,985 首，其中 SMC 190 首。正文必须按真实 inventory 改写，或按论文想声称的 SMC-only protocol 重跑。

#### B. selection objective 不匹配

CASM 当前 staged selection 综合：

- overall beat/downbeat 六项指标；
- metric guards；
- `six_metric_wins`；
- 历史参数距离/tie rule。

DBN 当前 selection 是：

1. 最大化 SMC Beat F1；
2. 保留距离最佳 F1 不超过 0.0005 的配置；
3. 再最大化 SMC CMLt；
4. 再最大化 SMC AMLt；
5. 再偏好离 default 较近的配置。

一个是在多 corpus、多 target、多 metric 下选“总体稳健配置”，另一个是在 SMC Beat 上选配置。即使它们最后在同一 test panel 上画 boxplot，selection pressure 也不同。

#### C. search space 不匹配

CASM 使用 staged structured search，并在 calibration-scale 实验中固定 30--300 support。

DBN 则搜索 52 个配置：

\[
\text{min BPM}\in\{30,55\},\quad
\text{max BPM}\in\{215,300\},
\]

再乘以 13 个 transition-lambda 值。

也就是说，DBN 被允许随 calibration subset 改变一个影响很大的 hard tempo support，而 CASM 没有。DBN 方差较大，可能部分来自“多了一个高风险选择自由度”，而不是 DBN 结构天生更不稳。

#### D. 相同 evaluation panel 是优点，但不足以消除上面三项混杂

两者都在固定 SMC fold0 和固定 GTZAN panel 上评分，这能保证 observed spread 来自“选出的配置不同”，而不是每次 test set 不同。

但固定 evaluation panel 不能让不同 calibration population、objective 和 search space 自动变得公平。

### 4. 一个直观类比

如果要比较两名学生“对复习材料抽样是否敏感”：

- 学生 A 每次看约 570 道跨学科题；
- 学生 B 每次只看 27 道同一科目题；
- A 按六项综合分选答案策略；
- B 先按一项主分数、再按两项 tie-break 选；
- B 还可以额外改变考试允许作答的题型范围。

最后即使二人都参加同一场考试，也不能把 A 成绩波动更小直接解释为“A 的思维结构天生稳定”。

### 5. 当前可以写什么，不能写什么？

可以写：

> Under their current, different calibration procedures and search spaces, the selected CASM configurations produce a narrower distribution of fixed-panel scores than the selected DBN configurations.

不能写：

> CASM is intrinsically less calibration-sensitive than DBN because it is semi-Markov/context-aware.

若要支持第二种因果主张，至少要：

- 用相同曲目；
- 用相同 primary metric/selection utility；
- 固定相同 tempo support，先只比较其他自由度；
- 匹配搜索 budget 或合理控制复杂度；
- 做 outer-fold rotation，而不是永久只用 SMC fold0；
- 在看结果前冻结 protocol。

---

## 三、CASM 依旧是 DP-based 吗？

**是，而且代码上没有歧义。**

### 1. DP 是什么？

DP 是 dynamic programming，中文“动态规划”。它不是一种神经网络，也不是“根据数据训练参数”的同义词，而是一种求解优化问题的算法。

它适用于具有 optimal substructure 的问题：如果“以候选 \(j\) 结束的最佳路径”经过前驱 \(i\)，那么到 \(i\) 的那部分一定也应当是“以 \(i\) 结束的最佳路径”。这样就不必枚举全部指数数量的 beat subsets，只需保存每个终点的最佳前缀分数。

### 2. CASM 的路径目标

候选事件按时间排序为 \(t_1,\ldots,t_N\)。路径

\[
\pi=(i_1,\ldots,i_K),\qquad i_1<\cdots<i_K
\]

的分数是

\[
\mathcal S(\pi)
=
\sum_{k=1}^{K}e_{i_k}
-
\sum_{k=2}^{K}D_{i_{k-1},i_k}.
\]

其中：

- \(e_j\) 是候选 \(j\) 的 activation evidence；
- \(D_{ij}\) 是相邻已选候选之间的 duration inconsistency cost；
- 只允许 tempo support 内的边。

### 3. 动态规划递推

令 \(S_j\) 为“所有以候选 \(j\) 结束的路径中，最高的分数”，则：

\[
S_j
=
e_j
+
\max\!\left(
0,\;
\max_{\substack{i<j\\(i,j)\text{ admissible}}}
[S_i-D_{ij}]
\right).
\]

这里外层的 0 表示：

- 如果所有前缀接过来都是负贡献，就从 \(j\) 重新开始；
- 这对应 v4 所说的 “restart after an unfavourable prefix”。

同时保存最佳前驱：

\[
P_j
=
\arg\max_i [S_i-D_{ij}].
\]

前向计算完后：

1. 从分数最大的终点开始；
2. 沿 \(P_j\) 反向回溯；
3. 反转顺序，得到最佳 beat path。

### 4. 与代码逐行对应

在 [`decoder.py`](../../src/casm_beat_tracking/decoder.py#L294)：

- 第 302--303 行：tempo range 转成合法 interval bounds；
- 第 304--308 行：

\[
e_i
=
\operatorname{clip}\!\left(
\frac{z^{\mathrm b}_{t_i}}{T},
-L,L
\right);
\]

- 第 313--322 行：列出每个终点的合法前驱；
- 第 324--335 行：计算 endpoint-symmetric target、confidence、sigma 与 \(D_{ij}\)；
- 第 336 行：`transition_scores = scores[starts] - duration_cost`；
- 第 339--341 行：只有最佳前缀为正才接入，否则 restart；
- 第 343--348 行：选终点并 backtrack。

这就是标准的 Viterbi-style / max-sum dynamic programming。

### 5. CASM 甚至有两次 DP

- beat path：稀疏 candidate graph 上的 segment-duration DP；
- downbeat path：选定 beat grid 上考虑 bar length 和 meter-change penalty 的第二个 DP，见 [`decoder.py`](../../src/casm_beat_tracking/decoder.py#L350)。

### 6. “semi-Markov”和“DP-based”是什么关系？

- **semi-Markov** 描述模型/打分结构：一次 transition 跨过一个可变长度的 candidate-to-candidate segment，并显式给整个 duration 打分；
- **DP-based** 描述求解方法：利用分解结构高效找到最高分路径。

因此 CASM 可以同时且正确地被称为：

> a sparse candidate-event semi-Markov decoder solved by dynamic programming

但要保留 v3 的 caveat：

- 它不是 generative HSMM；
- 不是 learned semi-CRF；
- 当前 segment potentials 没有通过梯度或最大似然训练。

---

## 四、CASM 与 PLPDP 的本质区别

### 1. 先承认共同点：二者的数学骨架很近

PLPDP 的递推为：

\[
D(n)
=
\Delta(n)
+
\max\left\{
0,\;
\max_{m<n}
\left[
D(m)
+
\lambda(n)P_{\hat\delta(n)}(n-m)
\right]
\right\},
\]

其中

\[
P_{\hat\delta}(\delta)
=
-
\left[
\log_2\!\left(\frac{\delta}{\hat\delta}\right)
\right]^2.
\]

把负号展开，它就是：

\[
\text{当前 evidence}
+
\max(
0,\;
\text{前缀分数}
-
\text{local-period inconsistency cost}
).
\]

CASM 的递推是：

\[
S_j
=
e_j
+
\max(
0,\;
S_i-D_{ij}
).
\]

所以二者都属于：

> activation evidence + input-conditioned local-period consistency + dynamic programming

这意味着以下新颖性表述不安全：

- “CASM 首次使用 DP 做 beat post-processing”；
- “CASM 首次把 local tempo/period 放进 DP”；
- “PLPDP 使用 global tempo，而 CASM 才使用 local tempo”。

这些说法都不成立。

### 2. 真正区别一：搜索域是 dense frames 还是 sparse candidates

| | PLPDP | CASM |
|---|---|---|
| DP state | 每个时间帧 \(n\) | 预先保留的 activation local maxima \(t_j\) |
| 可输出位置 | 原则上任意 frame | 只能是候选 local maximum |
| 主要行为 | local periodicity 可以补上 activation 很弱甚至没有明确峰的位置 | 只在已有 candidate evidence 中重新选择 |
| 风险侧重 | 提高 recall，但可能插入 false positives | 较保守；若真 beat 没成为 candidate，DP 无法凭空恢复 |

因此 v4 的 “recover weak beats” 最好限定为：

> recover weak but retained candidate maxima

而不是暗示 CASM 能在任意无峰位置插入 beat。

### 3. 真正区别二：局部周期从哪里来？

PLPDP：

- 用 STFT tempogram；
- 用多个长度的 sinusoidal kernels 构造 PLP；
- 默认组合 \(\kappa=1,3,5\) s 的 PLP；
- 从相邻 PLP peaks 得到 piecewise-constant local IBI \(\hat\delta(n)\)。

CASM：

- 在 beat activation 上做局部 normalized autocorrelation；
- 在 tempo-derived integer lag bank 中逐 lag 打分；
- 在候选位置取最大 lag 为 \(\tau_i\)；
- 当前默认用 8 s local window。

二者都估计 local period，但 estimator、时间平滑特性和 failure mode 不同。

### 4. 真正区别三：confidence 的语义

PLPDP 的 \(\lambda(n)\) 来自选中 PLP peaks 的高度/支持度。它描述“当前局部脉冲有多强”。

CASM 的

\[
c_i
=
\operatorname{clip}_{[0,1]}
\frac{q_i(\ell_i^\star)-q_i^{\mathrm{alt}}}
{|q_i(\ell_i^\star)|+\epsilon_c}
\]

显式比较：

- 最佳周期；
- 与最佳 lag 相距超过 \(\pm2\) 帧的最强竞争周期。

因此 \(c_i\) 更接近：

> dominant hypothesis 与 runner-up hypothesis 的相对分离度

这使它直接针对 half/double-time 等多模态 ambiguity，而不只是周期证据绝对高度。

### 5. 真正区别四：transition context 是单端还是双端

PLPDP 在当前 frame \(n\) 使用 \(\hat\delta(n)\) 和 \(\lambda(n)\) 评价从任意 \(m<n\) 到 \(n\) 的 transition。

CASM 对边 \((i,j)\) 使用：

\[
\bar\tau_{ij}=\sqrt{\tau_i\tau_j},
\qquad
c_{ij}=\sqrt{c_ic_j}.
\]

也就是 transition 同时参考 segment 两端的 local context。这个 endpoint-symmetric construction 是比“同样有 local period”更明确的结构差别。

### 6. 关于“strength 与 width”的必要数学澄清

CASM 写成：

\[
D_{ij}
=
\frac{\lambda c_{ij}}
{2[\sigma_0+(1-c_{ij})\sigma_u]^2}
\log^2\!\left(\frac{\Delta_{ij}}{\bar\tau_{ij}}\right).
\]

论文说 confidence 同时改变 constraint strength 和 tolerance/width，在参数解释层面是合理的：

- \(c\) 在分子调制强度；
- \(c\) 也通过 \(\sigma(c)\) 调制 tolerance。

但代数上两者最后合并成一个有效曲率：

\[
g(c)
=
\frac{\lambda c}{2[\sigma_0+(1-c)\sigma_u]^2},
\qquad
D_{ij}=g(c)\log^2(\cdot).
\]

也就是说，对固定中心 \(\bar\tau_{ij}\)，最终仍是一条由单个 scalar \(g(c)\) 缩放的 quadratic log-ratio curve。PLPDP 的 \(\lambda(n)\) 也缩放 quadratic log-ratio penalty。

因此不宜把以下说法当作 CASM 对 PLPDP 的“本质数学优势”：

> PLPDP only changes strength, while CASM uniquely changes both strength and width.

更稳妥的区别是：

> CASM uses a nonlinear mapping from a competitor-aware ambiguity margin to effective transition curvature, whereas PLPDP uses PLP-derived local pulse confidence as the coefficient of its local-period penalty.

### 7. 真正区别五：工程 safeguards 与 downbeat

CASM 还有：

- CASM/Direct event-count ratio 超界时返回 Direct；
- 在 beat grid 上做 meter-aware downbeat DP；
- downbeat DP 与 snapped direct downbeats 强烈不一致时回退。

PLPDP 原始核心是 beat tracker，没有相同的 CASM count-ratio 与 downbeat机制。当前实验 wrapper 中：

- 先将 50 Hz activation 插值到 PLPDP 所需 100 Hz；
- beat/downbeat probability 取 maximum 后送入 PLPDP；
- 仅在 released code 抛出特定异常时回退 Direct；
- downbeat 是实验 wrapper 另做 peak-picking 和 snapping。

wrapper 的这些步骤不应被写成 PLPDP 原论文的方法组成。

### 8. tempo range 不是 CASM 与 PLPDP 的分界

PLPDP 也不是 tempo-range-free：

- 原论文的 PLPDP/mHMM evaluation support 为 30--300 BPM；
- \(\kappa=1\) s kernel 用 60--300；
- \(\kappa=3,5\) s kernels 用 30--300。

CASM 当前也用 30--300 定义 local lag bank 和 legal transitions。

二者真正共同反对的是“单一固定 global tempo trajectory/rigidity 假设”，不是“所有可能周期都无限制地搜索”。

### 9. 最诚实的 novelty 定位

建议把 CASM 定位为：

> A sparse candidate-event, segmental DP decoder whose local duration potential is derived from a competitor-aware periodicity margin, symmetrized across segment endpoints, and protected by deterministic beat/downbeat safeguards.

而不是：

> A new local-period dynamic-programming paradigm.

前者能和 PLPDP 清楚区分；后者容易被审稿人用 PLPDP 的公式直接反驳。

---

## 五、为什么要恢复 v3 的公式？v4 究竟哪里不够？

### 1. v3 给出了可复现定义

[`casm_v3.0.tex`](../main/casm_v3.0.tex#L192) 明确写出：

\[
q_i(\ell)=
\frac{\left\langle a_u a_{u-\ell}\right\rangle_{u\in\mathcal W_i}}
{\sqrt{
\left\langle a_u^2\right\rangle_{u\in\mathcal W_i}
\left\langle a_{u-\ell}^2\right\rangle_{u\in\mathcal W_i}
+\epsilon_q}}
\left(\frac{\ell_{\min}}{\ell}\right)^\beta,
\]

并说明信号外 zero padding。

这与 [`decoder.py`](../../src/casm_beat_tracking/decoder.py#L98) 对应：

- `cross` 对应 \(\langle a_u a_{u-\ell}\rangle\)；
- `energy * shifted_energy` 对应两个能量项；
- `+ 1e-8` 对应 \(\epsilon_q\)；
- `(min_lag / lag) ** tempo_bias` 对应 fast-tempo prior；
- shifted array 初值为零，对应 zero padding；
- `uniform_filter1d(..., mode="constant")` 定义边界行为。

### 2. v4 不是写了“错误公式”，而是根本没有定义公式

[`casm_v4.tex`](../main/casm_v4.tex#L225) 只说：

> \(q_i(\ell)\) denotes the normalized autocorrelation score ... including a mild fast-tempo prior.

问题不是这句话与代码相反，而是它不足以唯一确定实现：

- normalized autocorrelation 是否减均值？
- 是 cosine normalization、Pearson correlation，还是 biased/unbiased autocorrelation？
- denominator 中 epsilon 放在根号内还是根号外？
- 窗口越界时 zero-pad、reflect 还是 truncate？
- fast-tempo prior 的函数形式是什么？
- prior 依赖 \(\ell_{\min}\) 还是绝对 lag？
- lag bounds 如何由 BPM 与 50 Hz 取整？

而后续 \(\tau_i\) 和 \(c_i\) 都依赖 \(q_i\)。所以从数学论文标准看，v4 把核心中间量变成了一个**有名字但不可复现的黑盒**。

### 3. tempo range 对两个模块的双重作用也应写明

v4 只明确说 edge \((i,j)\) 在 30--300 BPM 内才 admissible，却没有同样明确地说：

\[
\ell_{\min}
=
\max\left(
2,\left\lceil\frac{60F}{b_{\max}}\right\rceil
\right),
\qquad
\ell_{\max}
=
\min\left(
T-1,\left\lfloor\frac{60F}{b_{\min}}\right\rfloor
\right).
\]

同一个 tempo support 还定义 local autocorrelation 的 hypothesis bank。省略这一点会让读者误以为 range 只做最终 edge gating，也正是“CASM 是否可以完全不要 tempo range”容易产生误解的原因。

### 4. v4 还漏了 candidate evidence 的公式

v4 说 \(e_i\) 是 “clipped evidence score”，但没有定义。release code 实际为：

\[
e_i
=
\operatorname{clip}
\left(
\frac{z^{\mathrm b}_{t_i}}{T_e},
-L,L
\right).
\]

候选本身则从 sigmoid probability 的局部极大值中产生，并要求：

\[
a_{t_i}\ge\theta_c.
\]

这两个 threshold/scale 不是同一件事。建议写清楚，尤其因为 PLPDP 对 dense frames 打分，CASM 对 sparse candidates 打分，\(e_i\) 的定义关系到二者差异。

### 5. v3 的 caveat 应恢复

v3 明确写：

> It is not a generative hidden semi-Markov model, and the segment potentials are not learned.

这句话很重要，因为它防止审稿人把 “semi-Markov” 理解成：

- 训练了一个 HSMM；
- 训练了一个 semi-CRF；
- 学习了 segment emission/transition parameters。

v4 保留了 “semi-Markov structure”，却删掉 caveat，会增加不必要的命名争议。

### 6. 但绝不能“恢复整个 v3”

原因是：

- v3 当前主表也含相同的 SMC block 错配；
- v3 的旧结果段不等于 Frozen-7F 证据；
- v3 的 operating-point 历史与 v4 当前主张并不完全一致。

正确动作是选择性恢复：

| 项目 | 建议 |
|---|---|
| v3 local autocorrelation equation | 恢复 |
| zero-padding 与 lag rounding | 恢复/补全 |
| semi-Markov caveat | 恢复 |
| v3 first-5-s evaluation trim | 恢复 |
| v4 的 path/objective 结构 | 保留 |
| v4 的 confidence 与 endpoint formulas | 保留 |
| v3/v4 当前结果表 | 都不要作为可信源；从锁定输出重建 |

---

## 六、v4 methodology 还需要修的细节

### P0：会改变论文事实身份

1. **重建主结果表，不手工换格。**
2. **重写第 470 行的 “improves every metric”**：当前混合表不能支持 universal claim；即使重建后也要按新表逐格自动验证。
3. **校准数据描述纠正**：不要把 3,985 首多数据集 inventory 写成只由 190 首 SMC 构成。
4. **主 operating point 唯一化**：正文、表格、abstract、SOTA table 使用同一 config hash 和 range。

### P1：复现与数学边界

1. 恢复 \(q_i(\ell)\) 的完整公式；
2. 定义 \(\ell_{\min},\ell_{\max}\) 的取整和短序列 clipping；
3. 定义 \(e_i\)；
4. 写明 8 s window、5-candidate median filter 和 zero padding；
5. 明确“weak beat”必须已经进入 candidate set；
6. 恢复 non-generative/non-learned caveat；
7. evaluation protocol 恢复 first 5 s ignored；
8. caption 写清 Direct absolute / others delta；
9. 对 baseline wrapper 的 50→100 Hz resampling、probability combining、exception fallback 和 downbeat snapping 做 disclosure。

### P1：与 PLPDP 的 positioning

避免：

- “CASM 首次做 local periodicity DP”；
- “PLPDP 依赖 global tempo”；
- “CASM 没有 tempo range”；
- “CASM 可在完全无 activation evidence 的位置恢复 beat”。

推荐：

> Both PLPDP and CASM perform input-conditioned local-period dynamic programming. CASM differs by decoding a sparse activation-peak graph, estimating periodic ambiguity through a best-versus-competitor autocorrelation margin, symmetrizing context across segment endpoints, and integrating explicit beat/downbeat safeguards.

### P2：calibration sensitivity 图

在公平重跑前：

- 只作为 descriptive/exploratory；
- caption 明确 protocols differ；
- 不声称结构性 robustness。

若要进主文并做强比较：

- CASM/DBN 同 calibration tracks；
- 同 utility；
- 先固定共同 30--300 support；
- outer-fold rotation；
- 预先冻结 selection/search rules。

---

## 七、逐句回答这次的问题

### “v4 主表的 MSCNN/TCN CASM 与 DBN 数字疑似整行错配，什么意思？”

更正后的意思是：

> 不是整条九格 row 简单互换，而是 SMC 的三格 block 在 CASM 与 DBN 间精确交换；同一 row 的 GTZAN block 又来自另一配置，导致一行内的方法身份和 tempo-range 身份不统一。

### “这事咋回事？”

可确定的是 table assembly/provenance 出错；不可确定的是最初由手工复制、生成脚本还是旧文件命名引起。错误在 v4 建立之前的 v3 表里已经存在，v4 继承了它。

### “calibration protocol 不匹配是什么意思？”

CASM 与 DBN 的“选配置”过程用的曲目数量/构成、优化指标和可搜索参数不同，所以观察到的方差差异是整个 selection pipeline 的差异，不能直接归因于 decoder architecture。

### “我们的方法依旧是 DP based 的吗？”

是。beat decoding 是一次 max-sum DP，downbeat decoding 又是一次 meter-aware DP。

### “什么是 DP？”

DP 是 dynamic programming：保存“到每个候选终点为止的最佳前缀”，用递推和 backtracking 找全局最高分路径，从而避免枚举所有候选子集。

### “我们的方法和 PLPDP 的本质区别在哪？”

不是“有没有 DP”，也不是“有没有 local period”；二者都有。主要差别是：

- dense frame lattice vs sparse activation-peak graph；
- PLP-derived IBI/confidence vs autocorrelation best-versus-competitor ambiguity；
- destination-only context vs endpoint-symmetric segment context；
- 原始 beat-only core vs CASM 的 fallback 和 downbeat DP。

### “为什么要恢复 v3？”

只恢复 v3 中与代码一致、v4 为压篇幅而删掉的 \(q_i(\ell)\) 定义和 caveat。v4 的核心 duration equation 没错，但 local-period estimator 被写成不可复现的黑盒。v3 的表也有错，不能整体回退。

---

## 八、我的最终判断

1. **表格问题是 P0，必须先于任何性能结论修复。** 当前 v4 postprocessor table 不能被当作一张完整、单一 protocol 的结果表。
2. **CASM 确实是 DP-based semi-Markov decoder。** 这点在数学和代码上都成立。
3. **CASM 与 PLPDP 是近亲，不是范式对立。** 应把 novelty 放在 sparse candidates、competitor-aware ambiguity、endpoint-symmetric segment construction 与 safeguards 上。
4. **v4 methodology 的核心 objective/confidence/duration cost 基本正确，但 local-period 与 evidence 定义不足。**
5. **“恢复 v3”必须是 selective restoration，不是版本回滚。**
6. **calibration comparison 当前只能支持 protocol-level descriptive claim，不能支持 architecture-level causal claim。**

## 九、证据索引

- [v4 methodology](../main/casm_v4.tex#L195)
- [v4 主结果表](../main/casm_v4.tex#L334)
- [v3 local-autocorrelation 公式](../main/casm_v3.0.tex#L192)
- [当前 CASM local-period 实现](../../src/casm_beat_tracking/decoder.py#L98)
- [当前 CASM beat DP](../../src/casm_beat_tracking/decoder.py#L294)
- [当前 CASM downbeat DP](../../src/casm_beat_tracking/decoder.py#L350)
- [Frozen-7F release configuration](../../config/casm-7f-default.json)
- [calibration-scale 科学审计](2026-09-05_calibration_scale_scientific_audit.md)
- [PLPDP 全文中文翻译与公式](../reading/06_PLPDP_全文中文翻译.md#d-plp-与-dp-的结合)

### 外部归档路径

以下归档位于本机 project archive，不在当前 GitHub tree 内：

```text
/Users/jollibear/Work/pkb/30-projects/self-beat-mscnn/9 Archive/
  codex_outputs_raw/2026-09-04_casm_7f_tempo_range_blindspot_ablation/
```

关键文件：

- `table_postprocessor_ablation_7f_full.tex`
- `aggregate/aggregate_percent.csv`
- `aggregate/aggregate_exact.json`
- `aggregate/QA.json`
- `gadi_return/GADI_QA.json`
- `ARCHIVE_SHA256SUMS.txt`

这些文件是本报告中 Frozen-7F block identity 与 tempo-range 数字的依据。
