# Legacy evidence-script encoding boundary (2026-08-25)

## Outcome

Hardened `scripts/legacy_division_contract.py` so a source path containing
invalid UTF-8 is reported as a blocked contract input rather than leaking a
`UnicodeDecodeError` traceback. The source-level API converts the decoding
failure to `ValueError`, matching the existing missing-file, unreadable-file,
and syntax-validation boundary; the CLI returns status `2` with no stdout.

This changes only malformed-input handling. It does not normalize or rewrite
source files, import `tumor_ca.py`, run the model, generate figures, or choose
the unresolved `local_division_rate` semantics.

Classification: `INCREMENTAL` — dependency-light parsing boundary, with
empirical regression evidence.

## Verification

The isolated regression writes invalid bytes under pytest's `tmp_path` fixture
and verifies the CLI result without relying on repository state. The focused
legacy-contract suite passes, both edited Python files compile, and
`git diff --check` is clean. No model trajectory or figure-generation command
was run.

## Limit

The contract still intentionally requires UTF-8 source text. This change makes
that requirement explicit at the API/CLI boundary; it does not attempt encoding
detection or fallback parsing.
