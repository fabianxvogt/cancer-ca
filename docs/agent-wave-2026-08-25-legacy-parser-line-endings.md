# Legacy contract parser line-ending audit (2026-08-25)

## Audit scope

The source-only legacy contract probe was exercised with raw-byte fixtures
containing CRLF lines, mixed CRLF/LF lines, blank lines in a multiline source,
and more than one embedded NUL. The API and CLI boundaries were checked for
the same diagnostic, status `2`, empty stdout, and one-line stderr.

## Finding

No reproducible API/CLI defect was found. `Path.read_text(encoding="utf-8")`
normalizes the tested line endings before `ast.parse`; the existing diagnostic
wrapper therefore reports the same physical line and column for CRLF and mixed
line-ending fixtures. When several NULs are present, the first source NUL is
reported deterministically. Multiline syntax failures also remain a single
escaped `ValueError`/`CONTRACT BLOCKED` line.

## Change and evidence

No production parser behavior was changed. Regression tests now pin the
observed CRLF/multiline and mixed-ending API/CLI contract, including repeated
embedded NULs. The fixtures contain source text only: they do not import or
execute the model, generate figures, or interpret clinical semantics.

Verification requires the dependency-light legacy tests, Python compilation,
and `git diff --check`.

Classification: `INCREMENTAL / EMPIRICAL` — boundary audit and regression
coverage only; no scientific or clinical claim.
