# Historical and unselected figures

These files are preserved for design/provenance, **not** as additional
validated paper results. The directory mirrors the old paths to make the
original Git objects traceable:

- [`historical/gpt-figures/`](historical/gpt-figures/) — early candidate
  gallery and image variants.
- [`historical/self-run-figures/`](historical/self-run-figures/) — Figure 1
  cases, data-scaling experiments, Figure 2 candidate gallery, and other
  mechanism/ablation render variants.
- [`historical/Paper/`](historical/Paper/) — authors' old manuscript
  illustrations (`p0`–`p2`) from prior drafts; duplicated variants are kept
  at their original paths for provenance. The legacy `.jpg` files are actually
  PNG-encoded; [`legacy-paper-preview/`](legacy-paper-preview/) provides
  correctly suffixed copies for viewing online.
- [`source/`](source/) — available notebooks, plotting scripts, small figure
  payloads, and plot-input tables. Raw audio, full caches, and third-party
  reading material are not bundled.
- [`rejected-evaluation/`](rejected-evaluation/) — the old `fig03a` output
  removed from the active paper branch.

**Invalid-evaluation warning:** Historical Figure 3 ablation variants
(`fig03_ablation_matrix` and `fig03a`, including copies in candidate and
reference galleries) contain or derive from the `tcn_smc_final0` panel. That
TCN checkpoint trained on SMC and was evaluated on the same SMC set. These
graphics are retained only as rejected design/history artifacts. They must
not be cited, reused in the paper, or interpreted as held-out evidence.
Other historic figures have not been revalidated against the current
evaluation policy and should not be promoted without a fresh provenance
audit.
