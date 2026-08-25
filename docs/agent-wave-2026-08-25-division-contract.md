# Legacy division-gate contract (2026-08-25)

## Outcome

Added `scripts/legacy_division_contract.py`, a dependency-free AST probe that
reads `tumor_ca.py` without importing it. The probe reports the current raw
default multiplier (`4.0`), gate scale (`0.8`), and derived threshold (`3.2`),
including whether that threshold lies in the unit interval expected of a
Bernoulli probability.

This is a pre-calibration reproducibility guardrail. It does not clamp or
rescale the model, run a trajectory, calculate a metric, or support a
biological or clinical conclusion.

Classification: `INCREMENTAL` — semantics-contract infrastructure only.

The probe rejects boolean literals as numeric multipliers. Python treats `bool`
as an `int` at runtime, so accepting `True` would let a malformed source
contract pass validation while silently changing the reported gate scale. The
validator accepts only actual integer or floating-point AST literals; this is
input validation for the probe, not a semantic decision about the model.

## Verification

```text
python3 -m py_compile scripts/legacy_division_contract.py tests/test_legacy_semantics.py
python3 -m pytest -q -p no:cacheprovider tests/test_legacy_semantics.py
5 passed
python3 scripts/legacy_division_contract.py
```

The command reports the expected source contract, and the focused tests also
reject candidate sources that clamp the gate or use a boolean multiplier. No
model import, dependency overlay, figure generation, or generated artifact was
used.

## Limits and next test

The probe checks source syntax and the documented legacy constants only. It does
not establish that the raw threshold is a valid probability or that changing it
would preserve untreated trajectories. The next calibration experiment remains
an isolated rate sweep with seeded trajectory and replay comparisons before any
change to `tumor_ca.py`.
