# Legacy contract lambda/comprehension scope boundary (2026-08-25)

Classification: `INCREMENTAL / EMPIRICAL`

## Finding

The source-only contract probe correctly ignored comprehension loop targets and
lambda parameters, but it traversed lambda bodies as if they were part of the
declared method. A lambda-local assignment expression such as
`lambda: (division_prob := 0)` therefore caused a false duplicate-assignment
rejection. The same false rejection occurred when that expression was nested in
a comprehension inside the lambda.

Python's scope rules make two nearby cases different. An assignment expression
inside a comprehension directly in the method binds the containing method, so
`[(division_prob := 0) for _ in ()]` remains a blocked contract input. Lambda
defaults are also evaluated in the enclosing method and remain part of the
scan.

## Minimal fix

`_scoped_nodes()` now skips lambda bodies while continuing to scan lambda default
expressions. Existing comprehension-target handling remains unchanged because
those targets are not returned as method-scope binding positions.

## Evidence

- API coverage accepts lambda parameters, lambda-local assignment expressions,
  comprehension targets, and a comprehension-local assignment expression inside
  a lambda.
- API coverage rejects a method-level comprehension assignment expression and a
  lambda-default assignment expression.
- CLI coverage accepts the lambda-local assignment-expression fixture and emits
  the normal JSON report with no stderr output.
- All fixtures are source text only; neither `tumor_ca.py` nor any model or
  figure code is imported or executed.
- Dependency-light semantic tests, Python compilation, and `git diff --check`
  are required for this change.

This is an AST scope/reporting guard only. It does not establish model validity,
clinical meaning, or scientific reproducibility.
