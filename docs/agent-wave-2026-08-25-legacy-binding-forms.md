# Legacy contract method-scope binding forms (2026-08-25)

Classification: `INCREMENTAL / EMPIRICAL`

## Finding

The source-only legacy contract probe recognized ordinary assignment, annotated
and augmented assignment, `for` targets, and named-expression targets. It did
not recognize other Python bindings in the declared method scope. A candidate
source could therefore assign the reported `division_prob` through `with ...
as`, `except ... as`, an import alias, or a nested function/class name after the
formula assignment while the probe still reported the earlier expression.

## Minimal fix

The probe now inventories method-scope targets from `with`/`async with`,
`except ... as`, `for`/`async for`, import aliases, and nested function/class
definitions in addition to the existing forms. Tuple/list/starred targets are
checked recursively. Comprehension and lambda parameters are intentionally not
treated as method-scope bindings on the supported Python 3.9 runtime because
their targets remain in their own nested scope.

## Evidence

- API regressions cover `with ... as`, `except ... as`, an instance-attribute
  alias, import aliases, and nested function/class names.
- CLI regression confirms an exception alias returns status `2`, emits no JSON,
  and reports the established one-line blocked-contract message.
- Dependency-light semantic tests, Python compilation, and `git diff --check`
  are run for this change.

This is an AST parsing and reporting guard only. It reads source text and does
not import `tumor_ca.py`, run the cellular automaton, generate figures, or make
clinical or scientific claims.
