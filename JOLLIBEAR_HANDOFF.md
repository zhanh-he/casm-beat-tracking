# Historical release handoff for Jollibear

Current development is split between the `icassp2027` reproduction branch and
the `mirex2026` competition branch. The text below records the earlier
`paper-revisions` release handoff and is retained for provenance.

Date: 2026-09-28

Working branch: `paper-revisions`

## What changed

The repository was reduced to four reader-facing top-level areas:

- `casm/`: installable CASM package, frozen configuration, tests, API notes,
  and benchmarks.
- `experiments/`: method-specific experiment notes/code (`casm`, `dbn`,
  `crf`, `plpdp`, `beat_this`, `tcn`, and `mscnn`), the selected paper
  figures, and consolidated result tables.
- `online-demo/`: the complete static listening/visualization site and bundled
  public audio excerpts.
- `archive/`: a public explanation only. The full 133 MB manuscript, reading,
  presentation, and historical figure workspace remains local and is ignored
  by Git so it is not exposed or pushed.

Root metadata (`README.md`, `pyproject.toml`, `MANIFEST.in`, `.gitignore`, and
`.github/`) remains at the top level because packaging and automation require
it.

The three selected paper figures are now in `experiments/figures/`. The former
Figure 3 ablation material is under `experiments/tables/`, beside the LaTeX
table that replaced it.

## Validation already completed

- Package tests: **17 passed**.
- Frozen result-table validation: **4,556 pieces checked**, four public table
  artifacts rebuilt successfully.
- Wheel and source distribution: both built successfully and passed
  `twine check`.
- Local Markdown links: all checked successfully.
- Git patch hygiene: `git diff --check` passed.
- Live Pages site and its main CSS, JavaScript, data, visualization, and audio
  assets returned HTTP 200 on 2026-09-28.

## GitHub Pages migration

The live deployment was originally built from the old `main/docs` layout. The
new site is organized under `online-demo/`, and `.github/workflows/pages.yml`
now publishes that directory whenever `main` changes. All rendered site assets
are unchanged; only the demo README and manifest path metadata were updated for
the new layout.

On 2026-09-28, the repository Pages setting was migrated from
`legacy: main/docs` to `workflow: GitHub Actions` through GitHub's Pages API.
This prevents removal of the old `docs/` directory from breaking the site.
The equivalent setting in the UI is:

`Settings -> Pages -> Build and deployment -> Source -> GitHub Actions`

After merging, confirm that the `pages` workflow succeeds. Finally, hard-refresh
and verify:

<https://zhanh-he.github.io/casm-beat-tracking/>

Pushing `paper-revisions` itself is safe and will not change the live site; the
deployment workflow runs only on `main` (or by manual dispatch).

## Release notes / remaining decisions

- CASM is a decoder and has no learned neural checkpoint. Its frozen scalar
  configuration is packaged. Upstream front-end checkpoints are not bundled;
  `casm/weights/manifest.json` records expected external assets.
- A public software license has not yet been selected. Add `LICENSE` before a
  package release if redistribution terms need to be explicit.
- The `crf/` section is intentionally documentation-only because no sealed,
  standalone CRF artifact was present in the working tree.

## Suggested handoff sequence

1. Review this branch and `git status`.
2. Commit and push `paper-revisions`.
3. Confirm Pages Source still reads **GitHub Actions**.
4. Merge into `main`.
5. Watch the `pages` workflow and recheck the public URL.
