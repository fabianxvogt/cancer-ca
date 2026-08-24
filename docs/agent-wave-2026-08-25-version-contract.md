# Exact dependency-version contract (2026-08-25)

## Outcome

Strengthened `scripts/smoke_core_experiment.py` so the bounded smoke reads the
project's exact `name==version` pins, compares them with installed distribution
metadata, and reports the verified pins in JSON output. Missing distributions and
version drift now stop the smoke before `core_experiment` is imported.

Classification: `INCREMENTAL` — reproducibility infrastructure only. This change
does not alter the cellular automaton, calculate a metric, reproduce a correlation,
or support a biological or clinical conclusion.

## Verification

The dependency-light contract suite passed:

```text
python3 -m py_compile scripts/smoke_core_experiment.py tests/test_smoke_core_experiment.py
python3 -m pytest -q -p no:cacheprovider tests/test_smoke_core_experiment.py
6 passed
```

The dependency-light regression subset also passed:

```text
python3 -m pytest -q -p no:cacheprovider \
  tests/test_smoke_core_experiment.py tests/test_legacy_semantics.py
7 passed
```

The full local `tests/` collection is currently blocked before execution because
`tests/test_legacy_untreated.py` imports the absent `matplotlib` package. This is
consistent with the smoke's dependency preflight and is not a model failure.

The base interpreter's incomplete research environment remains explicitly blocked
by the smoke's dependency preflight. A complete scientific run still requires the
versions pinned in `requirements.txt`; the exact-version check does not establish
that those versions are behaviorally or scientifically sufficient.

## Empirical limits

- The contract verifies distribution metadata, not transitive native-library
  compatibility or numerical equivalence across platforms.
- The bounded smoke still checks only imports, strategy order, therapy-start
  metadata, and history lengths at its small fixed size and step count.
- No metric value, correlation, trajectory claim, theorem, biological effect, or
  clinical recommendation follows from this check.
