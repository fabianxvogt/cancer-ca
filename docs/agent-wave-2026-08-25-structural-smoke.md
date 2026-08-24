# Dependency-aware structural smoke (2026-08-25)

## Outcome

Added `scripts/smoke_core_experiment.py`, a reusable bounded entry point for
checking the core experiment's dependency surface, five strategy branches, and
history-shape contract. It lazily imports `core_experiment` only after checking
the pinned research dependencies and gives an install instruction when the
environment is incomplete.

Classification: `INCREMENTAL` — reproducibility/usability infrastructure only.
The command does not calculate response, stability, correlations, or any
biological result.

## Verification

Focused contract tests and syntax checks:

```text
python3 -m py_compile scripts/smoke_core_experiment.py tests/test_smoke_core_experiment.py
python3 -m pytest -q -p no:cacheprovider tests/test_smoke_core_experiment.py
3 passed in 0.01s
```

In the base Python 3.9.6 interpreter, where `scipy`, `matplotlib`,
`scikit-learn`, and `pandas` are unavailable, the entry point exits with status
2 and reports the pinned install command instead of exposing a transitive
import traceback. `--help` remains available without the research stack.

Using an isolated overlay populated from `requirements.txt`, the bounded
command was:

```text
PYTHONPATH=<overlay>:. MPLBACKEND=Agg MPLCONFIGDIR=<temporary> \
  python3 scripts/smoke_core_experiment.py --json
```

It returned status 0 with:

```json
{
  "history_lengths": [205],
  "seed": 42,
  "size": 32,
  "steps": 205,
  "strategies": 5,
  "therapy_start": 200
}
```

The same overlay ran the focused smoke tests plus the existing legacy tests:

```text
6 passed, 14 warnings in 1.20s
```

Warnings were Matplotlib/pyparsing deprecations from the temporary runtime;
they did not affect the checks.

## Empirical limits

- `size=32`, `steps=205`, and the core runner's fixed `radius=20` initialization
  are intentionally bounded and structurally oriented. They are not a
  representative model-scale run.
- Only importability, branch entry, strategy order, therapy-start metadata, and
  history lengths are checked. No metric value, correlation, trajectory claim,
  theorem, clinical interpretation, or biological conclusion follows.
- The smoke uses the pinned dependency versions in `requirements.txt`; it does
  not establish compatibility with other Python or library versions.
- The smoke suppresses the core runner's progress text and does not create
  figures, JSON result files, or other project artifacts.

## Files

- `scripts/smoke_core_experiment.py` — bounded command and structural validator.
- `tests/test_smoke_core_experiment.py` — dependency-light contract tests.
- `README.md` — reproduction command and scope note.
- `ROADMAP.md` — completed bounded-smoke usability item.
