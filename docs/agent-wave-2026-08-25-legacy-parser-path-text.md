# Legacy contract parser path-text diagnostics (2026-08-25)

## Audit scope

The source-only legacy contract probe was exercised with invalid Python
fixtures whose valid filesystem names contained Unicode line and paragraph
separators (`U+2028` and `U+2029`), literal backslashes, both quote styles,
trailing escape/tab/carriage-return controls, and a literal trailing
backslash. Each fixture was checked through the API and the CLI entry point.

## Finding

No reproducible API/CLI defect was found. Printable path text, including
backslashes and quotes, remains exact. Non-printable path text is rendered by
the existing line-safe escaping boundary, so Unicode separators and trailing
controls become visible escapes rather than output separators or terminal
controls. The API remains a `ValueError`; the CLI returns status `2`, emits no
stdout, and emits exactly one `CONTRACT BLOCKED` line on stderr.

## Change and evidence

No production parser behavior was changed. Regression coverage pins the exact
path display for every fixture and checks that API and CLI diagnostics agree,
remain printable, and contain exactly one terminating newline. The fixtures
only contain source text and do not import or execute the model, generate
figures, or interpret clinical semantics.

Verification requires the dependency-light legacy-contract tests, Python
compilation, and `git diff --check`.

Classification: `INCREMENTAL / EMPIRICAL` — deterministic parser-diagnostic
boundary coverage only; no scientific or clinical claim.
