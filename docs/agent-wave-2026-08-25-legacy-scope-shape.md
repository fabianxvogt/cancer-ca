# Legacy evidence-script scope and assignment-shape boundary (2026-08-25)

## Outcome

Hardened `scripts/legacy_division_contract.py` so each reported value comes
from its declared source scope and exact assignment target:

- `self.local_division_rate` must be assigned in
  `AdvancedTumorCA.__init__`.
- local `division_prob` must be assigned in
  `AdvancedTumorCA.rule_a_proliferation`.

The probe no longer treats an unrelated helper's local variable or an
arbitrary object's attribute with the same suffix as the legacy contract. It
also blocks annotated, augmented, chained, tuple, and other non-plain target
shapes that mention a contract name instead of interpreting them heuristically.

This changes only source-scope and malformed-input handling. It does not
import `tumor_ca.py`, run a trajectory, generate figures, or choose the
unresolved `local_division_rate` semantics.

Classification: `INCREMENTAL` — dependency-light parser validation, with
empirical regression evidence.

## Verification

The focused legacy-contract tests cover unrelated same-name decoys and wrong
receiver/local-target shapes. Python compilation and `git diff --check` remain
required checks. No model trajectory or figure-generation command is run.

## Limit

The contract intentionally recognizes only the two explicit source locations
and plain assignment forms documented above. Refactoring either model method
or changing the assignment shape should block the evidence probe until the
contract is reviewed.
