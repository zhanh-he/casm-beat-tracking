# CASM Beat Tracking Demo

## Public site

**https://zhanh-he.github.io/casm-beat-tracking/**

This is the public GitHub Pages demo. It can be opened directly without
cloning the repository or starting a local server.

The site presents finalized SMC 001/032/117/221 examples and four selected
GTZAN cases.

The page presents a public-view D3 visualization and synchronized Web Audio
audition for GroundTruth, Direct, DBN, PLPDP, and CASM. The offline reproduction
bundle retains the Fixed Semi-Markov mechanism comparison.
Clicks are synthesized from the frozen event arrays in `data/cases.json`.

One-click audition buttons sit in the decoder score table. Music is
streamed through the browser's native MP3 player; the click and music gains are
fixed, so the public interface only exposes the controls needed for comparison.

Each case includes its complete 30- or 40-second performance. GroundTruth and
every decoder overlay their events on exactly the same recording. SMC uses one
uniform beat click because it has no downbeat annotations; GTZAN retains beat
and downbeat click accents. The figure opens on a selected 12- or 18-second
analysis window, and the slider can audition every valid interval in each case.

The published clips and their provenance are documented in
[`audio/ATTRIBUTION.md`](audio/ATTRIBUTION.md).

## Generated assets

The published demo data and visualization are committed in this directory. The
historical generator and its frozen source bundle are retained under
`archive/figure-workspaces/`, but are not required to view or use the demo.

## Optional local preview

The following commands are only for development and are not needed to use the
public demo:

```bash
python -m http.server 8765 --directory online-demo
```

Then open <http://localhost:8765/>.

## Deployment and maintenance

GitHub Pages publishes this directory through
[`../.github/workflows/pages.yml`](../.github/workflows/pages.yml) after every
push to `main`; no generated site branch is maintained by hand. Keep page code,
case data, and public audio together here so a local preview matches the deployed
artifact.

Before merging a site change:

1. Preview `online-demo/` with the command above.
2. Confirm every path used by `index.html`, `app.js`, and
   `visualization.html` is relative to this directory.
3. Check the Pages workflow after the merge and verify the public URL with a
   hard refresh.
