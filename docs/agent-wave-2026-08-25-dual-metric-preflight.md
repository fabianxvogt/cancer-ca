# Dual-metric figure dependency preflight (2026-08-25)

Added a source-only preflight for `figure_S1_metric_dependence.py`. It parses the
figure's direct third-party imports and checks that each has a distribution mapping
and an exact `requirements.txt` pin before the bounded smoke inspects the runtime.

Classification: `INCREMENTAL` — dependency metadata guardrail only.

## Evidence

- The figure's direct third-party imports are `matplotlib`, `numpy`, and `scipy`.
- The current requirements file covers all three with exact pins.
- Focused tests exercise both the current contract and an unpinned-import failure
  without importing scientific packages or running the figure.

## Scope boundary

This preflight parses source and requirements text only. It does not import
scientific dependencies, execute the cellular automaton, generate a figure,
reproduce the sign-flip values, or establish scientific comparability.

The dual-metric roadmap item remains open because adding the result to the main
figures requires a separately verified numerical comparison.
