# Legacy contract parser diagnostics (2026-08-25)

## Finding

The source-only legacy contract probe passed `ast.parse` errors through to the
CLI with `str(SyntaxError)`. Python formats that string with only the basename,
so syntactically invalid `left/invalid.py` and `right/invalid.py` inputs both
reported `invalid.py, line 1`. An embedded NUL raised a separate parser
`ValueError` without any filename or line location. The API also exposed the
raw parser exception instead of the probe's established `ValueError` boundary.

## Change

Parser failures now become explicit `ValueError` results with the escaped exact
source path and parser line. Embedded NULs additionally report their column.
The CLI therefore keeps status `2`, no stdout, and a single deterministic
`CONTRACT BLOCKED` line while distinguishing same-basename files. The probe
still parses source only; it does not import or execute the model, generate
figures, or interpret clinical semantics.

## Evidence

- Source-only fixtures cover a nested syntax error at line 2 and an embedded
  NUL at line 3, column 5 through both `inspect_contract` and `main`.
- Dependency-light parser tests, Python compilation, and `git diff --check`
  are required before commit.

Classification: `INCREMENTAL / EMPIRICAL` — deterministic parser-diagnostic
hardening only. This does not establish scientific validity or calibrate
`local_division_rate`.
