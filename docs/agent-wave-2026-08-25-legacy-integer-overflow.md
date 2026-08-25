# Legacy contract integer-conversion boundary (2026-08-25)

## Finding

The source-level division contract already rejected non-finite float literals
and non-finite derived values. A syntactically valid, very large integer literal
was a remaining deterministic edge: converting the AST constant with
`float(...)` raised `OverflowError`, which escaped the API and leaked a traceback
from the CLI instead of producing the established blocked-contract response.

## Change

`legacy_division_contract.py` now converts that overflow into the same explicit
finite-multiplier `ValueError` used for non-finite numeric literals. The API
therefore reports a deterministic contract failure, and the CLI returns status
`2` with no JSON on stdout. This is a dependency-free parsing guard; it does not
import or execute the model, generate figures, or select a semantic
interpretation.

## Evidence

- A regression uses a 400-digit integer multiplier and verifies both the API
  exception and the CLI's status-2/stderr boundary.
- The focused legacy-contract suite, Python compilation, and `git diff --check`
  pass.

Classification: `INCREMENTAL / EMPIRICAL` — deterministic evidence-contract
hardening only. The guard does not establish scientific validity or calibrate
`local_division_rate`.
