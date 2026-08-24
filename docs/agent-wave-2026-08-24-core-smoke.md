# Core experiment smoke evidence (2026-08-24)

## Outcome

`core_experiment.run_controlled_experiment` completed a bounded, in-memory
smoke on a tiny grid. The smoke exercised all five strategy branches and
asserted complete histories without calling the analysis or visualization
functions. No project files were created or changed by the run.

Classification: `INCREMENTAL`. This validates importability and bounded
execution only; it is not evidence for the model's scientific claims.

## Dependency check

The base interpreter was Python 3.9.6 with NumPy 1.26.4 and pytest 8.4.2.
The base environment lacked the imports required by the core experiment:

- `scipy` — unavailable
- `matplotlib` — unavailable
- `scikit-learn` — unavailable
- `pandas` — unavailable

The smoke used an isolated temporary `pip --target` overlay, then removed it
after verification. The exact overlay versions were:

```text
numpy==2.0.2
scipy==1.13.1
matplotlib==3.9.4
scikit-learn==1.6.1
pandas==2.3.3
```

Runtime environment:

```text
MPLBACKEND=Agg
MPLCONFIGDIR=<temporary-overlay>/matplotlib
PYTHONPATH=<temporary-overlay>:/Users/fabian/Development/apps/cancer-ca
```

The project has no pinned dependency file. These versions are therefore a
reproducible probe environment, not a project-wide dependency decision.

## Smoke harness

The one-shot harness used this bounded call and assertions:

```python
from core_experiment import run_controlled_experiment

results = run_controlled_experiment(size=32, steps=205, seed=42)
assert len(results) == 5
assert [result["name"] for result in results] == [
    "MTD - Maximum Tolerated Dose",
    "Moderate Continuous",
    "Intermittent High",
    "Adaptive Low",
    "Metronomic",
]
for result in results:
    assert result["therapy_start"] == 200
    assert set(result["history"]) == {
        "sensitive", "resistant", "dead", "normal", "entropy",
        "edge_complexity", "total_tumor",
    }
    assert all(len(values) == 205 for values in result["history"].values())
```

The harness also compared `os.listdir(".")` before and after execution.

Exact smoke output:

```text
SMOKE PASS
python: 3.9.6
parameters: size=32, steps=205, seed=42
strategies: 5
history_lengths: [205]
project_files_changed: False
captured core output:

======================================================================
CORE EXPERIMENT: Response vs. Stability
======================================================================

Simuliere verschiedene Therapiestrategien...

  • MTD - Maximum Tolerated Dose...

  • Moderate Continuous...

  • Intermittent High...

  • Adaptive Low...

  • Metronomic...
```

## Existing-test verification

The two project tests were run explicitly with the same temporary overlay,
without pytest's cache plugin:

```text
PYTHONPATH=<temporary-overlay>:. MPLBACKEND=Agg \
MPLCONFIGDIR=<temporary-overlay>/matplotlib \
python3 -m pytest -q -p no:cacheprovider \
  tests/test_legacy_semantics.py tests/test_legacy_untreated.py
```

Result:

```text
3 passed, 14 warnings in 1.38s
```

The warnings were Matplotlib/pyparsing deprecations from the temporary
runtime; no test failed.

An unbounded `python3 -m pytest -q -p no:cacheprovider` discovery run was not
used as a completion gate. Repository research scripts such as
`reversibility_test.py` and several `scratch/*_test.py` files are collected as
tests; they start long parameter sweeps and require the additional undeclared
`seaborn` dependency. That run produced six collection errors for missing
`seaborn` and was interrupted after 143.13 seconds. This is a repository test
discovery limitation, not a failure of the bounded core smoke.

## Semantic limitations

The smoke is intentionally structural, not a miniaturized scientific
replication:

- `run_controlled_experiment` hard-codes `initialize_tumor(radius=20)`, so a
  32×32 grid is dominated by the initialization footprint and is not
  comparable to the default 120×120 setup.
- Every strategy starts therapy at step 200. The 205-step bound therefore
  covers only five active therapy steps; it verifies branch entry and return
  shape, not response/stability separation.
- The core function imports Matplotlib, SciPy, scikit-learn, and pandas even
  for this non-visual runner. A future maintainable smoke should either pin
  those dependencies or separate the import/runtime surface.
- `tumor_ca.py` was not changed. In particular, the documented raw
  `local_division_rate=4.0` and probability-like `0.8 * local_division_rate`
  semantics remain untouched.

No figures, JSON, PDFs, datasets, secrets, or generated artifacts were
created. Existing tests and documentation were preserved; the only intended
change is this evidence report.

## Next safe step

Pin the verified dependency set (or choose a supported alternative), then
consider exposing the tumor radius and therapy start as explicit test
parameters before adding a more representative small-grid numerical check.
