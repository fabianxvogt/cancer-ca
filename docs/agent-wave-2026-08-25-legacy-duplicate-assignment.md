# Legacy evidence-script duplicate-assignment boundary (2026-08-25)

## Outcome

Hardened `scripts/legacy_division_contract.py` so a source file with multiple
simple-name or attribute assignments for `local_division_rate` or
`division_prob` is reported as a blocked contract input. Previously the
dependency-free AST probe returned the first match and could hide a later
assignment that made the reported contract ambiguous.

This changes only malformed or ambiguous source handling. It does not import
`tumor_ca.py`, run a trajectory, generate figures, or choose the unresolved
`local_division_rate` semantics.

Classification: `INCREMENTAL` — dependency-light parser validation, with
empirical regression evidence.

## Verification

The isolated regression adds a second AST-valid `division_prob` assignment in
a temporary source file and verifies that the source-level API rejects it.
Focused legacy-contract tests, Python compilation, and `git diff --check` are
the required checks. No model trajectory or figure-generation command is run.

## Limit

The probe still intentionally recognizes only simple assignments to a name or
attribute and explicit numeric multiplication. Other AST forms remain blocked
by the existing contract rather than being interpreted heuristically.
