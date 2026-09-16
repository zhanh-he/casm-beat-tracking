---
title: CASM Related Work writing rationale
date: 2026-09-09
tags: [ICASSP, academic-writing, positioning, related-work]
---

# Related Work 写作思路与取舍

## 一句话策略

用第一段建立“全局结构解码与专门训练的 Direct 模型”两端，用第二段把 PLPDP 放到最接近 CASM 的中心位置，再以 dPLP 校正 ambiguity 新颖性边界，最后只用两句说清 CASM 的精确差异。

## 为什么写成两段

ICASSP 篇幅紧，Related Work 的任务不是复述整个领域，而是回答三个 reviewer 会立刻追问的问题：

1. CASM 相对标准 DP、CRF、DBN 和已有 semi-Markov rhythm tracker 在哪里？
2. CASM 相对 post-processing-free 或生成式 predictor 在哪里？
3. CASM 相对最近的 PLPDP、Real-Time PLP 和 dPLP 到底新在哪里？

两段正好对应“远邻背景”和“最近前身”。如果拆成三段，PLP 线会更舒展，但前两条路线会占用与论文贡献不成比例的版面。当前两段约 265 词，已经比原稿中三个 Related Work 小节紧凑很多。

## 每一段承担什么功能

| 位置 | 句子功能 | 为什么保留 |
| --- | --- | --- |
| 第一段前半 | DP、CRF、comb filter、DBN 的最小谱系 | 说明 CASM 处理的是已有的 activation-to-events 问题，不把 DBN 当成唯一历史起点。 |
| 第一段中部 | 用一句话承认已有 semi-Markov rhythm tracking | 防止标题被误读为对 semi-Markov 在节拍跟踪中的首创声明，同时不在 Related Work 展开技术推导。 |
| 第一段后半 | post-processing-free、Beat This!、masked diffusion | 交代 Direct 路线以及最新的多解建模；突出这些方法通常要求专门训练 predictor。 |
| 第一段末句 | frozen activation outputs | 给第二段的 plug-in decoder 比较设定定锚。 |
| 第二段开头 | PLP 到 PLPDP | 明确 PLPDP 是 closest line，而不是普通 baseline。 |
| 第二段中部 | PLPDP 已有 confidence；dPLP 已处理竞争周期 | 主动承认最接近的先行思想，减少 reviewer 认为论文回避文献的风险。 |
| 第二段末两句 | margin、strength+tolerance、count fallback、downbeat | 只保留足以划清方法边界的特征，数学定义留给 Methodology。 |

## 为什么 PLPDP 要这样“放进来”

PLPDP 最适合放在第二段的第二和第三句，并直接写成 closest line of work。先准确承认它的两个贡献：time-varying local IBI 与 confidence-weighted DP penalty；随后指出它的 confidence 是 absolute pulse strength，而非 period competition。这样写有三个好处：

- 不会把 PLPDP 歪曲成固定 tempo 或固定强度的 DP。
- 能自然导出 CASM 的 top-versus-competitor margin，而不是突然宣布一个没有文献坐标的新分数。
- 能把实验中的 PLPDP baseline 解释为真正的 nearest comparator，而不仅是多加一个后处理器。

dPLP 必须紧跟在 PLPDP 后面。它使“多个周期竞争”成为已经出现过的思想，因此正文主动写出 “CASM therefore does not claim ambiguity handling in general as new”。这句看似保守，实际会让后面的区别更可信：CASM 的价值来自 explicit margin、event-level segment path、separate Direct safeguard 和 frozen-backbone deployment 的组合。

## 对“ambiguity 高时退化到 Direct”的修正

用户原来的理解抓住了 CASM 的设计直觉，但不完全等于当前算法：

1. **局部软退化**：period margin 低时，duration cost 的权重下降、容忍区间变宽，所以结构化路径更接近 activation-led decoding。
2. **全局硬回退**：结构化输出与 Direct 的事件数比例越界时，count safeguard 才原样返回 Direct path。

因此论文最好写 “becomes increasingly activation-led under local ambiguity, while a separate count safeguard can return Direct”，不要写 “switches to Direct whenever ambiguity is high”。前者与公式和实现一致，后者会让 reviewer 寻找一个实际上不存在的 ambiguity threshold 或 routing rule。

## 为什么不在 Related Work 解释 semi-Markov

Related Work 只需要承认 Heydari et al. 已将 semi-Markov 用于高效、因果的 joint rhythm state-space modelling，并给出任务边界。CASM 的 sparse candidate graph、segment duration cost、复杂度和递推式属于“我们怎样做”，应留在 Methodology。这里如果展开，既重复方法，也会挤掉真正决定新颖性判断的 PLPDP/dPLP 比较。

## 我刻意避免的写法

- 不写 “the first ambiguity-aware decoder”。现有 dPLP 和 masked diffusion 都使该主张站不住。
- 不写 “PLPDP enforces a fixed periodicity”。这在事实层面错误。
- 不把 dPLP 或 Real-Time PLP 称为 PLPDP 的直接 sequel。它们延伸的是 PLP 表示本身。
- 不说 count safeguard 是由 ambiguity 直接触发。两个信号在当前算法中相互独立。
- 不把 resonating comb-filter 论文写成 joint beat/downbeat decoder。它提供的是显式周期估计。
- 不在 Related Work 报大段实验数字。数字属于 Experiments；这里只说明方法角色和已知 trade-off。

## 与 Introduction 的衔接建议

当前 Introduction 已经较详细地解释 DBN、Direct 和 PLPDP。若直接加入这版 Related Work，最容易出现的是 PLPDP 机制重复。建议按以下边界分工：

- Introduction 保留问题张力：Direct 的局部错误，DBN 的过强全局假设，以及一句“PLPDP 提供局部周期替代方案”。
- Related Work 承担准确谱系：PLPDP 如何使用 IBI 与 confidence，Real-Time PLP 和 dPLP 如何延伸这条线，CASM 与它们的边界。
- Methodology 再正式定义 top-versus-competitor margin、semi-Markov segment score 和 Direct count safeguard。

如果必须再省空间，优先删第一段的 CRF 和 comb-filter 句，不要压缩第二段。ICASSP reviewer 更可能根据 PLPDP 与 dPLP 判断 CASM 是否真的有新意。

## 投稿前最后检查

- 确认 BibTeX 中存在 `grosche2011plp`、`meier2024realtime`、`chiu2025dplp` 和 `foscarin2026masked`，并统一为论文当前的 key 命名规则。
- 将 masked diffusion 的 venue 状态写成与投稿时一致的版本。当前可核验状态为 2026 年论文，作者资料标注 ISMIR 2026。
- 确认实现中的 fallback 条件确实只有 event-count ratio；若还有直接由 ambiguity 触发的硬路由，应在 Methodology 和 Related Work 同步修改。
- 让 PLPDP baseline 的 tempo range、默认参数和 downbeat 处理方式在 Experiments 中保持可复现，Related Work 不承担这些实现细节。
- 检查 Introduction 不再重复第二段的 PLPDP 机制说明。
