# CASM 写作材料包——GPT-5.6 Sol 中文对照版

**整理日期：** 2026-09-13  
**写作模型：** GPT-5.6 Sol  
**源稿：** `/Users/hanyu/Documents/MacCodes/ICASSP2027/Paper/main/casm_v4.tex`

本目录是英文交付材料的中文对照版，方便逐段阅读和比较。LaTeX 命令、引用键、方法名和 BibTeX 字段尽量保持原样；中文 LaTeX 代码块仅供理解与取舍，不建议直接覆盖英文投稿稿件。源稿、论文、笔记和 reading 文件均未被修改。

## 文件

1. `01_version_A_balanced_recommended_zh.md`  
   推荐的完整方案：四段 Introduction、三部分 Related Work，以及修改后的 Fig. 1 表述。

2. `02_version_B_compact_zh.md`  
   面向严格 ICASSP 页数限制的最短方案。

3. `03_version_C_policy_narrative_zh.md`  
   更突出“由证据决定结构约束强度”以及 decoder 可迁移性的叙事方案。

4. `04_writing_rationale_and_proofread_zh.md`  
   中文写作 rationale、文献与段落对应关系、事实核查、Fig. 1 审查、calibration claim 边界及版本选择建议。

5. `05_bibtex_pack_zh.md`  
   必须补充的 BibTeX 条目、可选背景文献、现有 citation key 审计，以及 Masked Diffusion 的状态说明。

6. `06_updated_literature_notes_zh.md`  
   八篇本地 reading、DBN/PLPDP/dPLP 边界、structured decoder 历史和 claim 限制的中文笔记。

## 快速建议

论证最稳妥时从 Version A 开始。若追求更鲜明的表达，可采用 Version C 的 Introduction 加 Version A 的 Related Work；在 matched calibration 的 provenance 尚未确认前，结尾仍建议使用 A 的克制版本。按当前双栏全文版式，A/C 会形成 6 页并使 Introduction 尾段跨页；B 能把 Introduction 留在第 1 页，并将全文控制在 5 页。
