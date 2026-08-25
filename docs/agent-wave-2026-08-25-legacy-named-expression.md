# Legacy contract named-expression binding boundary (2026-08-25)

## Finding

The source probe rejected duplicate assignments and `for`-target rebindings,
but its AST scan did not treat named-expression targets as bindings. A valid
source file could therefore assign the expected `division_prob` formula and
later rebind that name with `division_prob := ...` while the evidence report
continued to accept the earlier assignment.

## Change

`legacy_division_contract.py` now scans `ast.NamedExpr.target` alongside the
existing assignment and loop-target forms. A named-expression target that
mentions either legacy contract value is rejected. The API raises `ValueError`;
the CLI returns status `2` without a partial report. This is a dependency-free
source-contract guard and does not import or execute the model, change figures,
or alter clinical semantics.

## Evidence

- A regression adds a named-expression rebinding of `division_prob` and verifies
  both the API error and the CLI's blocked, stdout-empty boundary.
- Dependency-light legacy-contract tests, source compilation, and
  `git diff --check` pass.

Classification: `INCREMENTAL / EMPIRICAL` — deterministic exact-source
contract hardening only. The guard does not establish scientific validity or
calibrate `local_division_rate`.
