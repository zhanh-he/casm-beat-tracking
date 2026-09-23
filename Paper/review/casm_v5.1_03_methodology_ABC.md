# CASM Methodology 怎么改：A / B / C 三个可选版本

**推荐：A。** `casm_v5.1.tex` 已采用 A 的结构。它保留 v5 最自然的叙述方式，同时恢复 v3 和当前代码中不可省略的定义。B 更像“给第一次接触方法的读者讲清楚”，C 更像页数极紧时的 camera-ready 压缩版。

## 三个版本都不能改变的技术事实

无论选 A、B 或 C，正文必须保持以下事实：

1. CASM 是 **offline sparse candidate-event decoder**；8-s centred window 使用未来 context。
2. candidate selection 使用 sigmoid activation 与 threshold；node score 使用 temperature-scaled clipped logit。
3. 30--300 BPM 同时限制 local lag bank 和 legal DP edges；它不是 per-track BPM input，但确实是 fixed hard support。
4. local period 是 normalized autocorrelation 的 argmax lag。
5. (c_i) 是 best lag 相对 strongest alternative（排除 `±2` lag frames）的 normalized margin，不是正确率概率。
6. CASM 只保留一个 selected period 和一个 scalar margin，不维护多条 tempo trajectories。
7. margin 通过 (c) 的乘法项和 (\sigma(c)) 共同改变一个 duration coefficient；不要说成三个独立可控的 `target/strength/tolerance` knobs。
8. (c\to0) 只会弱化 soft duration cost；candidate threshold、hard BPM support 和 sparse topology 仍存在。
9. exact Direct 只由 count-ratio safeguard 返回。
10. downbeat 在 selected beat grid 上用第二个 DP 解码；允许 meters 2--7，并有独立 agreement fallback。
11. `semi-Markov` 指 variable-duration candidate-to-candidate segment score；不是 generative HSMM，也不是 learned semi-CRF。
12. CASM 没有 trainable weights，但有 validation-selected global parameters；不能称 parameter-free。

## A / B / C 选择表

| 版本 | 主目标 | 公式完整度 | 人类可读性 | 页数 | 风险 | 建议用途 |
|---|---|---:|---:|---:|---|---|
| **A：v5 语言 + v3 精度** | 平衡解释、复现、novelty defense | 完整 | 高 | 中 | 最低 | **主稿推荐** |
| **B：两问驱动、图先行** | 第一次阅读最直观 | 完整但解释更长 | 最高 | 较长 | 图与公式可能重复 | 讲故事版；7F 图重生成后使用 |
| **C：camera-ready 压缩版** | 节省栏宽 | 最小充分 | 中 | 最短 | reviewer 需要查 config | 页数被卡死时 |

---

# Version A — v5 language with v3 precision（推荐）

## 结构

1. CASM overview
2. Candidate-event path
3. Local period and period competition
4. Ambiguity-conditioned duration cost
5. Decoding, safeguards, and downbeats

## 可直接替换的英文 LaTeX

```tex
\subsection{CASM overview}
CASM decodes a path through activation-supported beat candidates. At each
candidate, it asks two questions: which local period best explains the
surrounding activations, and how decisively does that period outrank its
strongest alternative? The selected period centres an event-to-event duration
preference, while the separation margin determines how strongly and narrowly
that preference is enforced. Like PLPDP, the preferred spacing is inferred
from the input; unlike a non-comparative peak-height confidence, CASM's margin
explicitly depends on a competing period. A separate count safeguard returns
Direct only when the complete structured path is implausibly sparse or dense.

\subsection{Candidate-event path}
A frozen tracker produces beat logits $z_t^{\mathrm b}$ at frame rate $F$,
with activations $a_t=\operatorname{sigmoid}(z_t^{\mathrm b})$. CASM retains
activation local maxima satisfying $a_t\geq\theta_{\mathrm c}$ as candidates
$\mathcal C=\{t_1,\ldots,t_N\}$. Candidate $i$ receives node evidence
\begin{equation}
e_i=\operatorname{clip}\!\left(z_{t_i}^{\mathrm b}/T_z,-L,L\right),
\end{equation}
where $T_z$ is a logit temperature and $L$ is the clipping bound. For $i<j$,
$\Delta_{ij}=(t_j-t_i)/F$. An edge is admissible only when its integer frame
interval falls within the fixed 30--300-BPM support. CASM selects an ordered
candidate path $\pi=(i_1,\ldots,i_K)$ by maximizing
\begin{equation}
\mathcal S(\pi)=\sum_{k=1}^{K}e_{i_k}
-\sum_{k=2}^{K}D_{i_{k-1},i_k},
\label{eq:casm-objective-a}
\end{equation}
where $D_{ij}$ scores the complete candidate-to-candidate duration. This
variable-duration segment score is the precise sense in which CASM is
semi-Markov. CASM is not a generative hidden semi-Markov model, and its segment
potentials are hand-specified rather than learned.

\subsection{Local period and period competition}
To estimate the local period, CASM compares a centred activation window with
lagged copies of itself. For fixed BPM bounds $B_{\min}$ and $B_{\max}$, the
admissible integer lags are
\begin{equation}
\ell_{\min}=\max\!\left(2,\left\lceil\frac{60F}{B_{\max}}\right\rceil\right),
\quad
\ell_{\max}=\min\!\left(T_{\mathrm{sig}}-1,
\left\lfloor\frac{60F}{B_{\min}}\right\rfloor\right).
\end{equation}
At candidate $i$, normalized local autocorrelation gives
\begin{equation}
q_i(\ell)=
\frac{\left\langle a_u a_{u-\ell}\right\rangle_{u\in\mathcal W_i}}
{\sqrt{\left\langle a_u^2\right\rangle_{u\in\mathcal W_i}
\left\langle a_{u-\ell}^2\right\rangle_{u\in\mathcal W_i}+\epsilon_q}}
\left(\frac{\ell_{\min}}{\ell}\right)^{\beta}.
\label{eq:casm-local-period-a}
\end{equation}
The implementation uses an 8-s centred window $\mathcal W_i$, zero padding
outside the signal, and a mild fast-tempo factor controlled by $\beta$. The
winning lag $\ell_i^\star=\arg\max_\ell q_i(\ell)$ defines
$\tau_i=\ell_i^\star/F$. The strongest distinct alternative excludes the
winning lag and its $\pm2$-frame neighbourhood:
\begin{equation}
q_i^{\mathrm{alt}}=\max_{\ell:\,|\ell-\ell_i^\star|>2}q_i(\ell),
\quad
c_i=\operatorname{clip}_{[0,1]}\!\left(
\frac{q_i(\ell_i^\star)-q_i^{\mathrm{alt}}}
{|q_i(\ell_i^\star)|+\epsilon_c}\right).
\label{eq:casm-margin-a}
\end{equation}
Thus, $c_i$ is a deterministic period-separation margin, not a calibrated
probability of correctness. A small margin means that another admissible lag
remains competitive; CASM does not retain that alternative as a second tempo
trajectory. Both $\tau_i$ and $c_i$ are median-filtered over five consecutive
candidates. The fixed BPM bounds therefore define both the local lag bank and
the admissible path edges.

\subsection{Ambiguity-conditioned duration cost}
For edge $(i,j)$, CASM symmetrizes the endpoint contexts as
$\bar\tau_{ij}=\sqrt{\tau_i\tau_j}$ and $c_{ij}=\sqrt{c_i c_j}$. It defines
\begin{equation}
\begin{aligned}
\sigma(c)&=\sigma_0+(1-c)\sigma_{\mathrm u},\\
w(c)&=\frac{\lambda c}{2\sigma(c)^2},\\
D_{ij}&=w(c_{ij})\log^2\!\left(\frac{\Delta_{ij}}{\bar\tau_{ij}}\right).
\end{aligned}
\label{eq:casm-duration-a}
\end{equation}
The log ratio treats proportional timing errors symmetrically. More
importantly, a small margin both broadens the tolerated deviation through
$\sigma(c)$ and reduces its weight through $w(c)$. A large margin therefore
favours candidate intervals near the selected period, whereas a small margin
moves CASM toward activation-dominated sparse-path decoding. Even when
$c_{ij}=0$ and the soft duration cost vanishes, the candidate restriction and
hard BPM support remain; the path is not necessarily identical to Direct.

\subsection{Decoding, safeguards, and downbeats}
A Viterbi-style dynamic program maximizes Eq.~\eqref{eq:casm-objective-a}.
For each candidate it links the best positive-scoring admissible prefix;
otherwise it restarts, and a final backtrace returns the highest-scoring path.
In parallel, Direct is formed using seven-frame max pooling on beat logits, a
zero-logit threshold, and one-frame deduplication. CASM returns this exact path
only if
\begin{equation}
\frac{|\pi_{\mathrm{CASM}}|}{|\pi_{\mathrm{Direct}}|}
\notin[r_{\min},r_{\max}],
\end{equation}
which detects an implausibly sparse or dense structured path. The release
configuration uses $[r_{\min},r_{\max}]=[0.85,1.8]$.

Downbeats are decoded only on the selected beat grid. A second dynamic program
links candidate downbeats using meters of 2--7 beats per bar and penalizes
meter changes. Direct downbeat maxima are independently snapped to the same
beat grid. If the event F-measure between the structured and snapped sequences
is below $0.6$ at a $70$-ms tolerance, CASM returns the snapped sequence; every
downbeat therefore coincides with an output beat. All scalar settings are
globally selected on development data and then frozen at inference. This is
supervised configuration selection, not learned decoder weights; inference
uses no reference annotations, externally supplied BPM or meter, or per-track
tuning.
```

## 为什么 A 最适合主稿

- 第一段先回答“它做什么”，读者不用先解公式。
- 第二段马上定义 candidate graph 与 semi-Markov 的真正含义。
- 第三段把 PLPDP--CASM 的区别落到可审计量：peak salience vs competitor margin。
- 第四段把 `strength` 和 `width` 拆开，能够直接承接 ablation。
- 第五段明确 `soft relaxation != Direct fallback`。
- 所有复现关键量都在正文，不依赖 reviewer 去猜代码。

---

# Version B — two questions, mechanism first（最易读）

## 适用条件

只有在 p0/p1 用 Frozen-7F 重生成后才建议使用 B。它依赖一张左右案例图把两种 operating regime 先讲清楚；旧 4F 图不能直接放回。

## 可直接替换的英文 LaTeX

```tex
\subsection{Two local questions}
At every plausible beat, CASM asks two questions: what local period best
explains the surrounding activations, and has that period won clearly enough
to trust? The first answer sets the preferred spacing between selected events.
The second determines how much that spacing should influence the decoded path.
This distinction matters because a pulse can be strong without being unique:
half- and double-time lags may both receive substantial support. CASM therefore
uses the winning period's advantage over its strongest competitor, rather than
the winning score alone.

Fig.~\ref{fig:casm-examples-7f} illustrates the two regimes. When one period
clearly wins, a stronger duration preference can connect weak but retained
activation maxima into a coherent path. When another period remains
competitive, CASM reduces that preference and lets node evidence decide more
of the path. The latter behaviour is soft relaxation, not fallback: the exact
Direct path is returned only by the separate count-ratio safeguard.

\subsection{Candidate path and local competition}
Let $z_t^{\mathrm b}$ be beat logits at frame rate $F$ and
$a_t=\operatorname{sigmoid}(z_t^{\mathrm b})$. CASM retains local maxima with
$a_t\geq\theta_{\mathrm c}$ as candidates $\mathcal C=\{t_i\}_{i=1}^N$ and
scores them by
\begin{equation}
e_i=\operatorname{clip}(z_{t_i}^{\mathrm b}/T_z,-L,L).
\end{equation}
It never inserts a beat away from this candidate set. The fixed 30--300-BPM
support defines integer lags
$\ell_{\min}=\max(2,\lceil60F/B_{\max}\rceil)$ through
$\ell_{\max}=\min(T_{\mathrm{sig}}-1,\lfloor60F/B_{\min}\rfloor)$ and also
defines which candidate-to-candidate edges are legal.

Within an 8-s centred, zero-padded window, CASM scores each lag by
\begin{equation}
q_i(\ell)=
\frac{\langle a_u a_{u-\ell}\rangle}
{\sqrt{\langle a_u^2\rangle\langle a_{u-\ell}^2\rangle+\epsilon_q}}
\left(\frac{\ell_{\min}}{\ell}\right)^\beta.
\end{equation}
The best lag gives $\tau_i=\arg\max_\ell q_i(\ell)/F$. With
$q_i^{\mathrm{alt}}$ denoting the best score outside a $\pm2$-frame
neighbourhood of the winner, the period-separation margin is
\begin{equation}
c_i=\operatorname{clip}_{[0,1]}\!\left(
\frac{q_i(\ell_i^\star)-q_i^{\mathrm{alt}}}
{|q_i(\ell_i^\star)|+\epsilon_c}\right).
\end{equation}
Both $\tau_i$ and $c_i$ are median-filtered over five candidates. The margin
is a deterministic relative score, not a calibrated probability and not a
second tempo trajectory.

\subsection{From local answers to one path}
For edge $(i,j)$, CASM combines its two endpoint contexts as
$\bar\tau_{ij}=\sqrt{\tau_i\tau_j}$ and $c_{ij}=\sqrt{c_ic_j}$. Its duration
cost is
\begin{equation}
D_{ij}=\frac{\lambda c_{ij}}
{2[\sigma_0+(1-c_{ij})\sigma_u]^2}
\log^2\!\left(\frac{\Delta_{ij}}{\bar\tau_{ij}}\right).
\end{equation}
Thus, a low margin both reduces the penalty amplitude and broadens its timing
tolerance. CASM selects the ordered candidate path maximizing
\begin{equation}
\mathcal S(\pi)=\sum_{i\in\pi}e_i-
\sum_{(i,j)\in\pi}D_{ij}.
\end{equation}
Each transition scores a complete variable-duration event segment; this is the
sense in which the decoder is semi-Markov. The potentials are deterministic
and hand-specified, not a generative HSMM or a learned semi-CRF.

\subsection{Safeguards and downbeats}
A Viterbi-style dynamic program supports restart after an unfavourable prefix
and backtracks the highest-scoring path. Direct is computed independently by
seven-frame max pooling, a zero-logit threshold, and one-frame deduplication.
If the CASM-to-Direct event-count ratio leaves $[0.85,1.8]$, CASM returns
Direct. Otherwise the structured path is retained even when its local margins
are small.

Downbeats are decoded on the selected beat grid by a second dynamic program
over meters 2--7 with a meter-change penalty. A separately snapped Direct
downbeat sequence replaces it only when their 70-ms event F-measure is below
0.6. The frozen decoder uses no reference annotations, per-track BPM or meter,
or trainable weights at inference.
```

## B 的优点与代价

优点：

- `what period?` / `has it won clearly?` 是最容易记住的核心；
- Figure 1 的左右案例自然对应两个问题；
- PLPDP 区别不需要一开始就堆术语。

代价：

- 比 A 多一个机制解释段；
- 图 caption、intro、method 容易重复；
- 如果没有 current-7F figure，叙述会失去支点。

---

# Version C — compact camera-ready（最省版面）

## 可直接替换的英文 LaTeX

```tex
\subsection{Sparse ambiguity-conditioned decoding}
Given beat logits $z_t^{\mathrm b}$ at frame rate $F$, CASM retains sigmoid
activation maxima above $\theta_c$ as candidates $\mathcal C=\{t_i\}$ and
assigns node score
$e_i=\operatorname{clip}(z_{t_i}^{\mathrm b}/T_z,-L,L)$. The fixed
$[B_{\min},B_{\max}]=[30,300]$ BPM support defines both the admissible local
lags and the legal candidate edges. In an 8-s centred, zero-padded window,
\begin{equation}
q_i(\ell)=
\frac{\langle a_u a_{u-\ell}\rangle}
{\sqrt{\langle a_u^2\rangle\langle a_{u-\ell}^2\rangle+\epsilon_q}}
\left(\frac{\ell_{\min}}{\ell}\right)^\beta,
\end{equation}
where
$\ell_{\min}=\max(2,\lceil60F/B_{\max}\rceil)$ and
$\ell_{\max}=\min(T_{\mathrm{sig}}-1,\lfloor60F/B_{\min}\rfloor)$.
The winning lag gives $\tau_i=\ell_i^\star/F$, and its normalized separation
from the best lag outside $\pm2$ frames is
\begin{equation}
c_i=\operatorname{clip}_{[0,1]}\!\left(
\frac{q_i(\ell_i^\star)-
\max_{|\ell-\ell_i^\star|>2}q_i(\ell)}
{|q_i(\ell_i^\star)|+\epsilon_c}\right).
\end{equation}
Both quantities are median-filtered over five candidates. The scalar $c_i$ is
a relative margin, not a calibrated correctness probability or a maintained
alternative trajectory.

For edge $(i,j)$, let
$\bar\tau_{ij}=\sqrt{\tau_i\tau_j}$,
$c_{ij}=\sqrt{c_ic_j}$, and
$\sigma(c)=\sigma_0+(1-c)\sigma_u$. CASM maximizes
\begin{equation}
\mathcal S(\pi)=\sum_{i\in\pi}e_i-
\sum_{(i,j)\in\pi}
\frac{\lambda c_{ij}}{2\sigma(c_{ij})^2}
\log^2\!\left(\frac{\Delta_{ij}}{\bar\tau_{ij}}\right)
\end{equation}
by Viterbi-style dynamic programming with restart and backtracking. Each edge
scores one variable-duration candidate segment, giving a hand-specified
semi-Markov objective. Low margin softens the duration term but leaves the
candidate graph and BPM support intact.

Direct is computed independently by seven-frame max pooling, a zero-logit
threshold, and one-frame deduplication; it replaces the structured path only
when their event-count ratio leaves $[0.85,1.8]$. A second beat-synchronous DP
decodes downbeats over meters 2--7 and falls back to Direct downbeats snapped to
the beat grid when 70-ms agreement falls below 0.6. All parameters are selected
globally and frozen at inference; CASM has no trainable weights or per-track
parameter fitting.
```

## C 不能再删什么

即使压页，也不要继续删除：

- (e_i) 的 logit 定义；
- (q_i(\ell)) 的 normalization；
- best-vs-alternative margin；
- hard BPM support 的双重作用；
- soft relaxation 与 Direct fallback 的区别；
- semi-Markov caveat。

可以移到 config/supplement 的只有具体 scalar 值、完整 downbeat recurrence 和 parameter table。

---

## 推荐插入的 PLPDP 对比段

无论选哪个版本，Introduction 或 Method overview 应保留一段这样的对比：

> PLPDP derives a time-varying IBI from the spacing of adjacent PLP peaks and weights its dense-frame dynamic-programming penalty by the mean height of the bounding PLP peaks. It therefore already adapts both the target and the weight of temporal regularization. CASM changes the conditioning signal and the search space: it compares the best local autocorrelation lag with the strongest non-neighbouring alternative, then uses this relative margin to control a duration cost on a sparse graph of retained activation maxima. The margin is neither a calibrated correctness probability nor a multi-hypothesis tempo trajectory.

这个版本承认 PLPDP 的真实贡献，又把 CASM 的 novelty 落在代码确实实现的地方。

## 推荐插入的 offline / deployment 边界句

> CASM is offline because its centred local window and global backtrace use future activation context. It requires no per-track BPM estimate or meter annotation, but it does use one validation-selected global configuration, a broad fixed period support, and a fixed meter inventory.

这比 `no tempo assumptions`、`parameter-free` 或模糊的 `uses future information to improve accuracy` 更准确。

## Ablation 名称怎样在 Methodology 中预先定义

若重跑 7F ablation，建议在结果表前增加：

> We isolate four choices in Eq.~(X). `Fixed precision' sets (c=1) after estimating the local target, removing all margin modulation. `Strength only' retains the multiplicative factor (c) but fixes (\sigma=\sigma_0). `Width only' lets (c) change (\sigma(c)) but removes the multiplicative factor. `One endpoint' replaces the geometric means by the destination candidate's period and margin. `No safeguards' disables both the beat-count and downbeat-agreement fallbacks.

这与历史脚本的实际含义一一对应：

| Ablation | 公式/代码变化 |
|---|---|
| Fixed precision | 估计 local period，但把 confidence/margin 设为 1 |
| Strength only | (D=\lambda c\log^2(\Delta/\tau)/(2\sigma_0^2)) |
| Width only | (D=\lambda\log^2(\Delta/\tau)/(2\sigma(c)^2)) |
| One endpoint | 使用 destination 的 (\tau_j,c_j)，不取 geometric mean |
| No safeguards | count ratio bounds 设为无穷；downbeat agreement threshold 设为 0 |

注意：这只是定义。v5 当前表仍混用 operating point；必须先重跑同一 7F full/variants，才能恢复结果解释。

## Figure caption 的 7F 推荐版

重生成 p0 后，可使用：

> **Illustrative CASM behaviour on real BeatThis out-of-fold activations from SMC.** Left: Direct retains mainly every second strong activation, whereas CASM uses a supported local period to select intervening retained maxima and recover a more continuous beat path. Right: competing octave-related period hypotheses yield a small margin and a weak duration coefficient, so the structured path happens to preserve the Direct events without invoking the count-ratio fallback. Reference IBI is shown only for interpretation and is never observed by the decoder. Tracks and 12-s windows were selected post hoc to expose the mechanism, not to estimate performance; every CASM beat remains anchored to a retained activation maximum.

重生成 p1 后，可使用：

> **Input-conditioned duration stiffness under the frozen-7F CASM configuration.** (a) The fixed constants map period margin (c) to coefficient (w(c)). (b) Selected path edges from different backbones and corpora occupy different parts of this response law. (c) Per-piece summaries show the resulting operating ranges; annotations report the separate count-ratio fallback rate. These panels audit decoder conditioning rather than tracking accuracy.

## 最终建议

- 主稿现在选 **A**；v5.1 已经这样实现。
- 7F p0/p1 重生成后，如果希望文章更“像人写的”，可以把 **B 的两问开头**移植到 A，后面仍保留 A 的完整数学结构。
- 只有在 ICASSP 页数真正不够时才用 **C**；不要为了省半栏再次回到 v5 那种省掉 (q_i(\ell))、(e_i) 和 hard-support 双重作用的状态。
