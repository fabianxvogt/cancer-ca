# Legacy contract report isolation (2026-08-25)

## Outcome

After the inspector matched the declared class/method scopes and exact
assignment shapes, its `inspect_contract()` result still exposed the module-level
owner-decision dictionary by reference. Mutating a nested list or field in one
returned report therefore changed later reports for the same source and made
otherwise identical JSON output call-order dependent.

The probe now deep-copies that metadata for every report. This is a reporting
and reproducibility guard only: it does not import `tumor_ca.py`, run a model
trajectory, generate figures, or select any unresolved calibration semantics.

Classification: `INCREMENTAL` / `EMPIRICAL`.

## Verification

`tests/test_legacy_semantics.py` mutates one returned report and verifies that a
fresh report has the original deterministic payload. Focused tests, compilation,
and `git diff --check` are required before commit.

## Limit

The guard isolates the inspector's returned metadata. It does not make source
files immutable or establish scientific validity for the legacy model.
