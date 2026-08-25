# Legacy target-reference boundary

Classification: `INCREMENTAL / EMPIRICAL`

## Finding

The legacy contract probe previously used `ast.walk()` over every assignment
target. That treated names and attributes inside target expressions as
bindings. A source-only candidate containing `lookup[self.division_prob] = 0`
after the real `division_prob` assignment was therefore rejected as having
multiple assignments, even though the assignment target is the lookup item and
`self.division_prob` is only a subscript expression.

## Minimal fix

`_mentions_target()` now follows only binding positions: direct `Name` and
`Attribute` targets, plus recursive tuple/list/starred unpacking. It does not
walk into `Subscript` values or slices. Actual nested rebindings such as
`(division_prob, other) = ...` and wrong receiver attributes remain blocked.

## Evidence

- API coverage accepts the subscript-expression case and still rejects a
  nested tuple rebinding.
- CLI coverage returns status `0`, emits the JSON report, and emits no stderr
  for the accepted case.
- Dependency-light semantic tests, compilation, and `git diff --check` are run
  for this change.

This is an AST parsing and reporting guard only. It reads source text and does
not import `tumor_ca.py`, run the model, generate figures, or make clinical or
scientific claims.
