# Manuscript asset contract (2026-08-25)

## Outcome

Added a dependency-free metadata contract linking `paper.tex`'s
`\includegraphics` paths and supplementary `Figure S<n>` mentions to the
committed image inventory. The inspected mismatch was that `paper.tex` discussed
committed Figures S2–S4 but did not include their image assets. The manuscript
now includes those existing PNGs; no figures were generated and no model or
scientific source changed.

Classification: `INCREMENTAL` — manuscript metadata/reproducibility only.

## Evidence

- Every `\includegraphics` path in `paper.tex` is present in `git ls-files`
  under `images/`.
- Every supplementary figure mention with a committed `figure_S<n>_...` asset
  has a matching included image.
- Focused contract tests pass without importing scientific dependencies.
- The contract does not inspect image contents or compile the manuscript.

## Scope and limits

The contract parses LaTeX tokens and reads Git's committed path inventory. It
does not validate captions, numerical claims, image contents, figure provenance,
PDF layout, or scientific comparability. The exploratory
`figure_S1_metric_dependence.py` source remains intentionally outside the paper
asset inventory because it has no committed rendered artifact.
