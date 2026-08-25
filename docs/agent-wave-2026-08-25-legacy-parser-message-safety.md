# Legacy contract parser message safety (2026-08-25)

## Audit scope

The source-only legacy contract probe was exercised with fixtures containing
raw C0 controls, an escape character inside an unterminated string, a Unicode
line separator, a mismatched delimiter, and a malformed f-string. These cases
were selected because Python's parser can expose source context through
`SyntaxError.text` and can use less-common message forms such as f-string and
delimiter diagnostics.

## Finding

No reproducible API/CLI defect was found. The parser messages observed in the
fixture set contained no raw control characters, and the existing wrapper
already uses only `exc.msg` plus the exact path and line rather than rendering
`SyntaxError.text`. The API therefore remains a one-line `ValueError`, while
the CLI returns status `2`, no stdout, and one line of `CONTRACT BLOCKED`
stderr for every fixture.

## Change and evidence

No production parser behavior was changed. Regression tests now derive the
current parser message from each source-only fixture, verify that the API
preserves that message and location without source controls, and verify the
same one-line CLI boundary. The fixtures do not import or execute the model,
generate figures, or interpret clinical semantics.

Verification requires the dependency-light legacy-contract tests, Python
compilation, and `git diff --check`.

Classification: `INCREMENTAL / EMPIRICAL` — deterministic parser-diagnostic
boundary coverage only; no scientific or clinical claim.
