# Legacy contract loop-rebinding boundary (2026-08-25)

## Finding

The source probe rejected duplicate plain assignments, but its AST scan did
not treat `for` targets as bindings. A valid source file could therefore
assign the expected `division_prob` formula and later rebind that name in a
loop while the evidence report continued to accept the earlier assignment.
That made the exact source contract incomplete for a deterministic shadowing
case.

## Change

`legacy_division_contract.py` now scans `for` targets alongside plain,
annotated, and augmented assignments. A target that mentions either
legacy contract value is rejected unless it is the one required plain
assignment. The API raises `ValueError`; the CLI returns status `2` without a
partial report. This is a dependency-free source-contract guard and does not
import or execute the model, change figures, or alter clinical semantics.

## Evidence

- A regression adds a loop target rebinding `division_prob` and verifies both
  the API error and the CLI's blocked, stdout-empty boundary.
- Focused legacy-contract tests, Python compilation, and `git diff --check`
  pass.

Classification: `INCREMENTAL / EMPIRICAL` — deterministic exact-source
contract hardening only. The guard does not establish scientific validity or
calibrate `local_division_rate`.
