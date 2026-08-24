# Required-import pin coverage

Classification: `INCREMENTAL` — dependency/reproducibility contract only.

## Change

The bounded smoke now checks that each distribution named by its required
scientific-import map has an exact `name==version` entry in `requirements.txt`.
The check normalizes packaging separators and runs before dependency discovery or
model import.

## Evidence

- Focused smoke-contract tests: 8 passed; legacy semantics tests: 2 passed.
- The current `requirements.txt` has no required-import pin gaps.
- `python3 -m py_compile scripts/smoke_core_experiment.py tests/test_smoke_core_experiment.py` passed.
- `git diff --check` passed.
- The bounded smoke is blocked in the base interpreter by missing `scipy`,
  `matplotlib`, `scikit-learn`, and `pandas`; it exits before model import.

## Scope and limits

This is `FORMAL` metadata validation of the repository's declared import-to-pin
map. It does not install or import scientific dependencies, execute the model,
compare trajectories, reproduce paper metrics, or establish scientific
comparability. The base interpreter remains unable to run the bounded model smoke
until the pinned environment is installed.

Unfiltered repository-wide test discovery is not a valid base-interpreter gate:
it collects legacy and scratch modules that import the scientific stack and
fails at collection for the same missing dependencies. The dependency-light
targets above remain independently runnable.

## Next test

Run `python3 scripts/smoke_core_experiment.py --json` inside the pinned dependency
environment. That will test installed availability and exact versions, then run
only the existing bounded structural smoke; it must not be interpreted as a
scientific replication.
