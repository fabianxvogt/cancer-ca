# Direct source-import pin coverage (2026-08-25)

Added a dependency-light AST contract to the bounded smoke. It parses the direct
third-party imports in `core_experiment.py`, excludes the two local project modules,
and verifies that each remaining import has a distribution mapping and an exact
`requirements.txt` pin.

Classification: `INCREMENTAL` — source/metadata guardrail only.

## Evidence

- Direct imports currently resolve to `matplotlib`, `numpy`, and `pandas`.
- The current requirements file covers all three with exact pins.
- Focused contract tests pass without importing scientific packages.
- The base interpreter still blocks the model smoke because `scipy`, `matplotlib`,
  `scikit-learn`, and `pandas` are unavailable.

## Scope boundary

This contract parses source and requirements text only. It does not import scientific
dependencies, execute the cellular automaton, compare trajectories, reproduce paper
metrics, or establish scientific comparability.

## Next test

After installing the exact pinned environment, run:

```text
python3 scripts/smoke_core_experiment.py --json
```

Interpret the result only as the existing bounded structural smoke, not as scientific
replication.
