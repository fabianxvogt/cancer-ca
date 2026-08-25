# Legacy contract path error-message boundary (2026-08-25)

## Finding

The dependency-free legacy contract CLI included the raw `--path` text in
blocked-contract messages. A syntactically valid path containing a newline
therefore split one error into multiple output lines, and a syntax error could
leak the same control character through `SyntaxError` formatting. That made
line-oriented stderr capture ambiguous even though the exit status was
deterministic.

## Change

The inspector now renders non-printable path text with `repr` before using it in
source-read errors or as the parser filename. Ordinary printable paths retain
their existing messages. This is an error-reporting boundary only: it does not
import or execute the model, generate figures, or select a semantic
interpretation.

## Evidence

- Dependency-light API/CLI regressions cover missing and syntactically invalid
  paths containing a newline.
- Both cases return status `2`, emit no stdout, and keep stderr to one line
  with an escaped path.
- Python compilation and `git diff --check` are required before commit.

Classification: `INCREMENTAL / EMPIRICAL` — deterministic error-message
hardening only. The guard does not establish scientific validity or calibrate
`local_division_rate`.
