# Manuscript reference contract (2026-08-25)

Added a dependency-light metadata check for LaTeX cross-references in `paper.tex`.
The contract requires every `\\ref{...}` token to have a matching `\\label{...}`
token in the manuscript.

The inspected gap was unambiguous: the manuscript referenced
`fig:phase_diagram`, but no such label or committed figure artifact existed. The
adjacent source instead defines `tab:phase_boundaries`, so the manuscript now
points to that existing table while retaining the schematic/non-computed caveat.

Classification: `INCREMENTAL` — metadata/reproducibility infrastructure only. No
model source, scientific result, clinical language, private data, generated figure,
or image contents changed.

## Evidence

- `manuscript_reference_gaps()` parses manuscript reference/label tokens without
  importing scientific packages or running scripts.
- Focused contract and legacy-semantics tests pass: 19 tests.
- Python syntax compilation and `git diff --check` pass.

## Limits

This contract does not compile `paper.tex`, verify PDF inclusion, inspect image
contents, compare numeric results, or support a biological or clinical claim.
