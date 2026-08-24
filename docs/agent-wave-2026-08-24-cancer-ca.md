# Agent wave: cancer-ca calibration gate (2026-08-24)

## Scope and outcome

Added the smallest focused regression guard for the documented untreated legacy
trajectory. No model behavior was changed. `tumor_ca.py`, `core_experiment.py`,
figures, JSON data, and manuscript artifacts were not edited or regenerated.

## Changed paths

- `tests/test_legacy_untreated.py` — two `unittest` cases pin a six-step 9×9,
  radius-1 untreated trajectory for seed 7, same-seed replay, final-grid
  fingerprint, and different-seed divergence.
- `docs/agent-wave-2026-08-24-cancer-ca.md` — this evidence record.

`ROADMAP.md` contains the matching completed regression checkbox while leaving
rate calibration and the separate small-grid core smoke test open; it has no
separate remaining diff in this scoped handoff.

An adjacent existing `tests/test_legacy_semantics.py` was observed during final
inspection and was left untouched.

## Runtime assumptions

- The available interpreter is `python3`, Python 3.9.6; `python` is not
  installed in this environment.
- The base interpreter has NumPy 1.26.4 but lacks SciPy, Matplotlib, and
  scikit-learn, which `tumor_ca.py` imports at module load time. pandas is also
  absent and is imported by `core_experiment.py`.
- The focused test was therefore run with an isolated temporary dependency
  overlay: NumPy 2.0.2, SciPy 1.13.1, Matplotlib 3.9.4, scikit-learn 1.6.1,
  and pandas 2.3.3. No overlay files are in this project.
- `MPLBACKEND=Agg` is set so importing the research module does not require a
  display.

## Exact focused test and result

Dependency setup used only a temporary directory:

```text
probe_deps=$(mktemp -d)
python3 -m pip install --quiet --target="$probe_deps" scipy matplotlib scikit-learn pandas
```

Focused command:

```text
PYTHONPATH="<temporary dependency overlay>:." MPLBACKEND=Agg python3 -m unittest discover -s tests -p 'test_legacy_untreated.py' -v
```

Result:

```text
test_seeded_trajectory_and_replay_match_legacy_behavior (test_legacy_untreated.LegacyUntreatedTrajectoryTests) ... ok
test_untreated_trajectory_remains_seed_sensitive (test_legacy_untreated.LegacyUntreatedTrajectoryTests) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.035s

OK
```

## Interpretation

The selected untreated setup produces total-tumor counts
`(10, 20, 33, 50, 70, 80)` over six steps for seed 7. Replaying with seed 7
produces the same grid; seed 8 produces a different grid and trajectory.
Current semantics are therefore stochastic across seeds but deterministic for a
fresh run that resets the global NumPy seed through `AdvancedTumorCA(seed=...)`.
This is a reproducibility statement for the pinned setup, not a claim that the
model is structurally deterministic or statistically robust.

The documented `local_division_rate` behavior remains untouched: the default
raw value is 4.0 and the division comparison uses `0.8 * local_division_rate`
as a probability-like threshold. The regression does not calibrate or rescale
that value.

## Classification

`INCREMENTAL` — a reversible, empirical guardrail that preserves legacy
behavior before calibration. It is not evidence of a biological result,
novelty, or parameter validity.

## Limitations

- Coverage is intentionally narrow: one grid size, one radius, six steps, and
  two seeds; it does not validate the 120×120 core experiment.
- The exact grid fingerprint depends on the NumPy/analysis dependency stack;
  versions are recorded above because the project currently leaves versions
  unpinned.
- The base environment cannot import the model without the documented
  research dependencies.
- No generated figures, JSON data, PDF output, credentials, or model source
  were changed.

## Next calibration experiment

In an isolated comparison harness, sweep `local_division_rate` around the
legacy default on the same 9×9 untreated setup and record (a) the raw gate
`0.8 * local_division_rate`, (b) six-step seeded trajectories, and (c)
same-seed replay across the supported dependency environments. Compare the
observed gate semantics with the intended Bernoulli probability scale before
any change to `tumor_ca.py`; then rerun the focused regression and a separately
approved small-grid core smoke test against representative outputs.
