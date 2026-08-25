# Legacy contract derived-finiteness boundary (2026-08-25)

## Finding

The source-level division contract already rejected negative-form literals and
non-finite numeric literals before reporting a result. It did not, however,
check arithmetic derived from individually finite constants. A positive
subnormal gate scale could make the saturation boundary overflow to `Infinity`,
and a large finite scale could overflow one of the calibration thresholds.
The CLI previously returned status 0 with a non-standard JSON non-finite value.

## Change

`legacy_division_contract.py` now rejects non-finite default thresholds,
calibration thresholds, and saturation boundaries as blocked contract inputs.
The API raises `ValueError`; the CLI returns status 2 with no report on stdout.
This is a dependency-free reporting guard and does not import or execute the
model, change figures, or choose a semantic interpretation.

## Evidence

- Focused legacy-contract tests cover negative and non-finite literals, both
  derived overflow cases, API errors, and CLI output suppression.
- Python compilation and `git diff --check` pass.

Classification: `INCREMENTAL / EMPIRICAL` — deterministic evidence-contract
hardening only. The guard does not establish scientific validity or calibrate
`local_division_rate`.
