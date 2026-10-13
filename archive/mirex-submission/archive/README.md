# CASM figure archive

This public archive preserves our figure outputs and selected plotting
materials. It is deliberately split so that the figures currently selected
for the paper appear first:

1. [`01-used/`](01-used/) — exact copies of the three current paper-facing
   figures in [`../experiments/figures/`](../experiments/figures/), plus
   historical plotting code and relevant small inputs.
2. [`02-unused/`](02-unused/) — earlier self-rendered outputs, candidate
   galleries, old manuscript illustrations, and their available source
   materials. These are **not** current paper results.

Every archived binary/source file has a SHA-256 and original Git-object
reference in [`MANIFEST.json`](MANIFEST.json). Run
`python archive/verify_archive.py` from the repository root to check that
all archived files are present and unchanged. Git history is retained, so
the original paths can also be inspected.

The old full research workspace is **not** stored here. Raw audio, third-party
reading PDFs, model checkpoints, virtual environments, and large experiment
caches are excluded. Some historic plotting bundles therefore cannot be
fully rerun from this curated archive alone; their README files describe the
available inputs and missing dependencies. The old Figure 3 ablation
visualization includes an in-sample TCN–SMC panel and is archived only under
`02-unused/` with an explicit invalid-evaluation warning. Do not use it as
benchmark evidence.
