# Figure-script dependency pin coverage (2026-08-25)

## Outcome

Extended the dependency-aware source contract to every committed `figure*.py`
script. The import-to-distribution map now includes `seaborn`, which is already
exactly pinned in `requirements.txt` and is used by the parameter-space figure.
The preflight remains metadata-only and runs before dependency discovery or model
import.

Classification: `INCREMENTAL` — reproducibility infrastructure only. This change
does not alter the cellular automaton, execute a figure script, regenerate an
artifact, or support a biological or clinical conclusion.

## Evidence

- All seven committed figure scripts have zero direct-import pin gaps.
- The focused smoke and legacy-semantics contract tests passed: 15 tests.
- `python3 -m py_compile scripts/smoke_core_experiment.py
  tests/test_smoke_core_experiment.py` passed.
- `git diff --check` passed.

## Scope and limits

The contract parses source and `requirements.txt` text only. It does not import
scientific dependencies, execute trajectories, generate figures, compare numeric
outputs, reproduce paper metrics, or establish scientific comparability. Exact
distribution pins also do not guarantee transitive native-library compatibility
or cross-platform numerical equivalence.

The dependency-aware bounded smoke still requires the exact environment in
`requirements.txt`; the base interpreter may stop before model import when those
dependencies are unavailable or drifted. In the current Python 3.9.6 base
interpreter, it stops before model import because `scipy`, `matplotlib`,
`scikit-learn`, `pandas`, and `seaborn` are unavailable; no packages were
installed for this change.
