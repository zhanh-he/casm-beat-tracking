# CASM bibliography pack 中文说明版

**整理模型：** GPT-5.6 Sol  
**核对对象：** `main/casm.bib`、本地论文与翻译，以及可用的第一方出版页面  
**用途：** 为修改后的 Introduction 和三段 Related Work 提供 BibTeX 条目与 citation-key 状态说明

## 1. 必须加入 `casm.bib` 的条目

三个版本都会引用 `grosche2011plp`，但当前 `casm.bib` 中没有这个 key。这是拟议正文唯一必须新增的条目。

```bibtex
@Article{grosche2011plp,
  author={Grosche, Peter and M{\"u}ller, Meinard},
  title={Extracting Predominant Local Pulse Information from Music Recordings},
  journal=ieee-taslp,
  volume={19},
  number={6},
  pages={1688--1701},
  year={2011},
  doi={10.1109/TASL.2010.2096216},
}
```

核对来源：[FAU publication record](https://cris.fau.de/publications/224409325/)。

## 2. 可选的背景条目

如果之后希望更直接地引用 human-listening opening、expressive-performance 历史或 experiment-audit 讨论，可以使用以下条目。目前 Versions A--C 均不要求加入它们。

```bibtex
@InProceedings{grosche2010difficult,
  author={Grosche, Peter and M{\"u}ller, Meinard and Sapp, Craig Stuart},
  title={What Makes Beat Tracking Difficult? A Case Study on Chopin Mazurkas},
  booktitle=ismir,
  pages={649--654},
  address={Utrecht, The Netherlands},
  year={2010},
}
```

核对来源：[official ISMIR 2010 paper](https://archives.ismir.net/ismir2010/paper/000110.pdf)。

```bibtex
@InProceedings{chiu2023experimentissues,
  author={Chiu, Ching-Yu and M{\"u}ller, Meinard},
  title={What Can Go Wrong When Conducting Beat Tracking Experiments},
  booktitle={Demos and Late Breaking News of the International Society for Music Information Retrieval Conference (ISMIR)},
  address={Milan, Italy},
  year={2023},
}
```

核对来源：[official ISMIR 2023 program record](https://ismir2023program.ismir.net/lbd_325.html)。

## 3. `casm.bib` 中已经存在的核心 keys——不要重复粘贴

| Key | 当前在 `casm.bib` 中的大致位置 | 状态 |
| --- | ---: | --- |
| `foscarin2024beat` | 约第 892 行 | 已存在 |
| `ellis2007beattracking` | 约第 940 行 | 已存在 |
| `korzeniowski2014crf` | 约第 964 行 | 已存在 |
| `krebs2015dbn` | 约第 984 行 | 已存在 |
| `bock2015combfilter` | 约第 992 行 | 已存在 |
| `bock2016joint` | 约第 1000 行 | 已存在 |
| `heydari2022semimarkov` | 约第 1062 行 | 已存在 |
| `chen2022postprocessingfree` | 约第 1071 行 | 已存在 |
| `chiu2023localperiodicity` | 约第 1079 行 | 已存在 |
| `meier2024realtime` | 约第 1089 行 | 已存在；volume、pages 和 DOI 正确 |
| `chiu2025dplp` | 约第 1111 行 | 已存在；pages 198--205 正确 |
| `foscarin2026masked` | 约第 849 行 | 已存在；camera-ready 前需再次核对出版状态 |

两项近期 PLP 工作的第一方核对页面：[TISMIR volume 7](https://transactions.ismir.net/7/volume/7/issue/1) 和 [ISMIR 2025 proceedings list](https://ismir.net/conferences/ismir-2025/)。

## 4. 出版状态仍需更新的条目：Masked Diffusion

当前 bibliography 把 `foscarin2026masked` 写成 ISMIR 2026 的 in-proceedings paper。截至 2026-09-13，公开 arXiv record 已经存在，但本次核对没有找到最终 proceedings 页面和页码。如果作者已经确认录用，现有条目可以保留，并注明 pages pending。若在 proceedings metadata 发布前需要一个可以公开核验的版本，请用下面的条目**替换**现有条目，而不是重复添加：

```bibtex
@Misc{foscarin2026masked,
  author={Foscarin, Francesco and Korzeniowski, Filip and Vogl, Richard},
  title={Masked Diffusion Enables Coherent Beat Tracking},
  year={2026},
  eprint={2608.04624},
  archivePrefix={arXiv},
  primaryClass={cs.SD},
  note={Accepted at ISMIR 2026; proceedings metadata pending},
}
```

公开记录：[arXiv:2608.04624](https://arxiv.org/abs/2608.04624)。

## 5. Related Work 的 citation map

- 第 1 段——structured decoding：`ellis2007beattracking`、`korzeniowski2014crf`、`fillon2015crf`、`bock2015combfilter`、`krebs2015dbn`、`bock2016joint`、`heydari2022semimarkov`。
- 第 2 段——PLP lineage：`grosche2011plp`、`chiu2023localperiodicity`、`meier2024realtime`、`chiu2025dplp`。
- 第 3 段——alternative approaches：`hainsworth2004particle`、`heydari2021beatnet`、`heydari2024beatnetplus`、`pinto2021userdriven`、`maia2022adapting`、`chen2022postprocessingfree`、`foscarin2024beat`、`foscarin2026masked`，并可选用 `ahn2025beatfcos`、`bolt2026reformulated`。

如果页数迫使删减 citations，优先删除第 3 段中的可选旁支。不要删除 `grosche2011plp`、`chiu2023localperiodicity`、`chiu2025dplp` 或 `heydari2022semimarkov`；这四项最直接地保护论文的 novelty boundary。
