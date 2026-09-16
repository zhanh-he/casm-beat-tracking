# CASM bibliography pack

**Prepared by:** GPT-5.6 Sol  
**Checked against:** `main/casm.bib`, the local papers/translations, and available first-party publication pages  
**Purpose:** BibTeX entries and key-status notes for the revised Introduction and three-paragraph Related Work

## 1. Required addition to `casm.bib`

All three draft versions cite `grosche2011plp`, but that key is absent from the current `casm.bib`. This is the only new entry required by the proposed text.

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

Verification: [FAU publication record](https://cris.fau.de/publications/224409325/).

## 2. Optional contextual entries

These entries are useful if you later cite the human-listening opening, expressive-performance history, or experiment-audit discussion more directly. None is required by Versions A--C as currently written.

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

Verification: [official ISMIR 2010 paper](https://archives.ismir.net/ismir2010/paper/000110.pdf).

```bibtex
@InProceedings{chiu2023experimentissues,
  author={Chiu, Ching-Yu and M{\"u}ller, Meinard},
  title={What Can Go Wrong When Conducting Beat Tracking Experiments},
  booktitle={Demos and Late Breaking News of the International Society for Music Information Retrieval Conference (ISMIR)},
  address={Milan, Italy},
  year={2023},
}
```

Verification: [official ISMIR 2023 program record](https://ismir2023program.ismir.net/lbd_325.html).

## 3. Core keys already present — do not paste duplicates

| Key | Current location in `casm.bib` | Status |
| --- | ---: | --- |
| `foscarin2024beat` | around line 892 | present |
| `ellis2007beattracking` | around line 940 | present |
| `korzeniowski2014crf` | around line 964 | present |
| `krebs2015dbn` | around line 984 | present |
| `bock2015combfilter` | around line 992 | present |
| `bock2016joint` | around line 1000 | present |
| `heydari2022semimarkov` | around line 1062 | present |
| `chen2022postprocessingfree` | around line 1071 | present |
| `chiu2023localperiodicity` | around line 1079 | present |
| `meier2024realtime` | around line 1089 | present; volume/pages and DOI are correct |
| `chiu2025dplp` | around line 1111 | present; pages 198--205 are correct |
| `foscarin2026masked` | around line 849 | present; publication status needs final camera-ready check |

First-party checks for the two recent PLP entries: [TISMIR volume 7](https://transactions.ismir.net/7/volume/7/issue/1) and [ISMIR 2025 proceedings list](https://ismir.net/conferences/ismir-2025/).

## 4. Status-sensitive entry: Masked Diffusion

The current bibliography records `foscarin2026masked` as an ISMIR 2026 in-proceedings paper. As of 2026-09-13, the public arXiv record is available, but a finalized proceedings page/pagination was not located during this check. If acceptance is author-confirmed, the existing entry can remain with a note that pages are pending. If you need a publicly verifiable entry before proceedings metadata appears, use the following **instead of**, not in addition to, the current entry:

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

Public record: [arXiv:2608.04624](https://arxiv.org/abs/2608.04624).

## 5. Citation map for the proposed Related Work

- Paragraph 1, structured decoding: `ellis2007beattracking`, `korzeniowski2014crf`, `fillon2015crf`, `bock2015combfilter`, `krebs2015dbn`, `bock2016joint`, `heydari2022semimarkov`.
- Paragraph 2, PLP lineage: `grosche2011plp`, `chiu2023localperiodicity`, `meier2024realtime`, `chiu2025dplp`.
- Paragraph 3, alternatives: `hainsworth2004particle`, `heydari2021beatnet`, `heydari2024beatnetplus`, `pinto2021userdriven`, `maia2022adapting`, `chen2022postprocessingfree`, `foscarin2024beat`, `foscarin2026masked`, and optionally `ahn2025beatfcos`, `bolt2026reformulated`.

If space forces citation cuts, remove optional branches from paragraph 3 first. Do not remove `grosche2011plp`, `chiu2023localperiodicity`, `chiu2025dplp`, or `heydari2022semimarkov`; those four protect the paper's novelty boundary most directly.
