# AI-owned project documentation

Use this folder for concise, reviewable notes maintained by coding agents: verified setup, architecture, validation commands, and bounded cleanup plans.

The project README and any document marked `human-owned` remain authoritative. Do not overwrite human-owned material or make unsupported claims.

Never store credentials, private data, generated output, logs, datasets, or build artifacts here. Preserve unrelated local work and keep each change focused.

## Decision and review map

The latest owner disposition for all three open lanes is recorded in
[`roadmap-review-2026-08-25.md`](roadmap-review-2026-08-25.md). It is a documentation
and evidence-boundary note; it does not close a scientific roadmap item.

- **Dual metric:** the [sign-flip probe](agent-wave-2026-08-25-dual-metric.md) is an
  incomplete runtime attempt, while the [dependency preflight](agent-wave-2026-08-25-dual-metric-preflight.md)
  is metadata-only.
- **Rule ablation:** there is no separate decision memo; section 2 of the consolidated
  roadmap review is the current disposition, and no ablation contract is approved.
- **Calibration:** the [`local_division_rate` decision memo](decision-memo-local-division-rate.md)
  keeps all three semantic readings open pending owner choice.
  The [bounded sensitivity audit](agent-wave-2026-08-25-division-semantics-sensitivity.md)
  compares the legacy rule with one documented unit-interval screen, preserving
  the owner-decision boundary and making no biological claim. Its reduced
  Adaptive arm preserves the source's absolute cutoff, so it is a bespoke
  closed-loop fixture rather than a scale-equivalent core-policy reproduction.
- The [Adaptive semantics × cutoff factorial](agent-wave-2026-08-25-adaptive-semantics-factorial.md)
  adds three paired seeds, a capacity-fraction cutoff comparison, and
  cross-yoked dose paths. Its 24 executions contain 16 unique tumor
  trajectories and four unique dose paths, including eight exact replay checks.
  Bounded response contrasts remain under the shared scaled all-high path,
  while their seed-level direction is unstable.

## Deferred calibration finding

The local research scripts currently expose a scale mismatch: `local_division_rate` is used as a probability-like threshold, but the observed calculation is not guaranteed to remain in the unit interval. Untreated trajectories also use deterministic choices, so changing that scale or introducing stochastic behavior could alter existing results and published figures.

This is a documented follow-up, not a behavior change. Before changing the model, calibrate the scale against the intended probability semantics, add regression coverage for untreated trajectories, and compare representative outputs. Do not modify the pre-existing untracked `tumor_ca.py` or research artifacts as part of this note.

### Guardrail for interpretation

`local_division_rate` is a raw multiplier used as a probability-like threshold: the current gate compares a random draw with `0.8 * local_division_rate`. The default `4.0` therefore yields `3.2`, making the division gate deterministically eligible when nutrient and empty-neighbor conditions also pass. Later mutation, placement, and death steps remain stochastic. This documents legacy behavior for reproducibility; it does not claim structural robustness or justify rescaling the model.

## Focused regression check

Run `python3 -m pytest -q tests/test_legacy_semantics.py` before changing the
division-rate scale. The test intentionally captures the current default gate;
calibration work should replace it only after comparing untreated trajectories.

The bounded core smoke used the versions pinned in [`../requirements.txt`](../requirements.txt).
It validates importability and branch execution on a small grid, not the
scientific conclusions of the full experiment.

The reusable command is `python3 scripts/smoke_core_experiment.py`; its output
and empirical limits are recorded in
[`agent-wave-2026-08-25-structural-smoke.md`](agent-wave-2026-08-25-structural-smoke.md).
The command also verifies that installed distribution versions exactly match
`requirements.txt`; this is an environment contract, not a claim that the model
is scientifically validated.

The smoke checks required-import pin coverage before inspecting the interpreter.
That check only compares the static import-to-distribution map with exact entries
in `requirements.txt`; it does not import dependencies, run the model, or imply
that results are scientifically comparable. Its evidence is recorded in
[`agent-wave-2026-08-25-pin-coverage.md`](agent-wave-2026-08-25-pin-coverage.md).

It also parses the direct third-party imports in `core_experiment.py` and every
committed `figure*.py` script, checking that each has a mapped exact pin. This
source/metadata contract does not import packages, execute a trajectory, generate
figures, or establish scientific comparability. Its figure coverage includes the
supplementary metric-dependence script. Evidence is recorded in
[`agent-wave-2026-08-25-source-pin-coverage.md`](agent-wave-2026-08-25-source-pin-coverage.md)
and [`agent-wave-2026-08-25-figure-pin-coverage.md`](agent-wave-2026-08-25-figure-pin-coverage.md).

The unresolved semantic choice is captured in the
[`local_division_rate` decision memo](decision-memo-local-division-rate.md).
It compares probability, rate/propensity, and legacy eligibility-score
interpretations and specifies the smallest pinned-environment experiment after
human approval. It does not change the model or claim biological validity.

The same preflight parses the existing exploratory dual-metric source,
`figure_S1_metric_dependence.py`, and checks its direct imports against the same
exact pins. This does not execute the source or verify its numerical results. Its
evidence is recorded in
[`agent-wave-2026-08-25-dual-metric-preflight.md`](agent-wave-2026-08-25-dual-metric-preflight.md).

## Manuscript reference contract

The structural smoke parses `paper.tex` for LaTeX `\\ref{...}` and `\\label{...}`
tokens and fails on undefined references. This is a metadata-only consistency
check: it does not compile the manuscript, import scientific dependencies, execute
figure scripts, inspect image contents, or validate the reported results. The
current evidence is recorded in
[`agent-wave-2026-08-25-manuscript-figure-contract.md`](agent-wave-2026-08-25-manuscript-figure-contract.md).

It also checks that every manuscript `\\includegraphics` path is committed and
that each mentioned supplementary figure with a committed asset is actually
included. This is a metadata-only asset check; its evidence is recorded in
[`agent-wave-2026-08-25-manuscript-asset-contract.md`](agent-wave-2026-08-25-manuscript-asset-contract.md).

## Calibration contract probe

Run `python3 scripts/legacy_division_contract.py` to inspect the legacy division
gate without importing dependencies or executing the model. The JSON report keeps
the raw default multiplier and gate scale explicit, expands the memo's four-rate
table (`0.5`, `1.0`, `1.25`, `4.0`), identifies the saturation boundary, and
repeats the exact owner decision boundary while leaving the semantic choice
unset. The focused tests guard this source contract. It is a pre-change evidence
probe, not a probability calibration or scientific validation.

The probe also treats non-UTF-8 source bytes as blocked input: the API raises
`ValueError` and the CLI returns status `2` with no report on stdout. This is a
parsing and reproducibility guard only; it does not normalize source files or
execute the model. Evidence is recorded in
[`agent-wave-2026-08-25-legacy-encoding-boundary.md`](agent-wave-2026-08-25-legacy-encoding-boundary.md).

It rejects more than one assignment for either contract field instead of
silently selecting the first AST match. It also requires the exact declared
scope and target shape: `self.local_division_rate` in
`AdvancedTumorCA.__init__`, and local `division_prob` in
`AdvancedTumorCA.rule_a_proliferation`. This keeps unrelated same-name decoys,
wrong receivers, and malformed assignment shapes blocked without changing
model behavior; evidence is recorded in
[`agent-wave-2026-08-25-legacy-scope-shape.md`](agent-wave-2026-08-25-legacy-scope-shape.md).

The returned owner-decision metadata is deep-copied per report. This prevents a
caller mutating one nested report field from changing later reports for the same
source, preserving deterministic JSON output. Evidence is recorded in
[`agent-wave-2026-08-25-legacy-report-isolation.md`](agent-wave-2026-08-25-legacy-report-isolation.md).

The probe also rejects a zero gate multiplier before calculating the saturation
boundary. This keeps invalid source contracts as explicit `ValueError` API
results and status-2 `CONTRACT BLOCKED` CLI responses instead of leaking a
division-by-zero traceback.

It also rejects finite source constants whose derived default threshold,
calibration threshold, or saturation boundary overflows to a non-finite value.
This keeps the dependency-free JSON report finite and deterministic; evidence is
recorded in [`agent-wave-2026-08-25-legacy-derived-finiteness.md`](agent-wave-2026-08-25-legacy-derived-finiteness.md).

Very large integer literals are also treated as blocked finite-multiplier input
when Python cannot convert the AST value to a float. The API raises `ValueError`
and the CLI returns status `2` without a traceback or partial JSON report; this
boundary is documented in
[`agent-wave-2026-08-25-legacy-integer-overflow.md`](agent-wave-2026-08-25-legacy-integer-overflow.md).

Non-printable characters in a source path are escaped in blocked-contract error
messages, including parser errors, so line-oriented stderr remains one-line and
deterministic. Printable paths retain their existing display. This is a
reporting-only guard; evidence is recorded in
[`agent-wave-2026-08-25-legacy-path-error-boundary.md`](agent-wave-2026-08-25-legacy-path-error-boundary.md).

Parser diagnostics also retain the exact escaped source path instead of Python's
basename-only `SyntaxError` rendering, and normalize syntax/NUL parser failures
to the API's `ValueError` boundary. Line numbers are preserved and embedded NULs
include a column. This keeps same-basename fixtures distinguishable without
importing or executing the model. Evidence is recorded in
[`agent-wave-2026-08-25-legacy-parser-diagnostics.md`](agent-wave-2026-08-25-legacy-parser-diagnostics.md).

The follow-up line-ending audit covers raw CRLF, mixed CRLF/LF, multiline
source, and repeated embedded-NUL fixtures. No additional API/CLI defect was
reproduced; the regression coverage pins the existing deterministic first-NUL,
line-safe status-2 boundary. Evidence is recorded in
[`agent-wave-2026-08-25-legacy-parser-line-endings.md`](agent-wave-2026-08-25-legacy-parser-line-endings.md).

The parser safety follow-up also exercises raw C0 controls and Unicode line
separators in source, an unterminated string containing an escape character,
mismatched delimiters, and a malformed f-string. The wrapper keeps only the
parser message and location, not `SyntaxError.text`, so API errors and CLI
stderr remain one-line and free of source control characters. No additional
defect was reproduced; evidence is recorded in
[`agent-wave-2026-08-25-legacy-parser-message-safety.md`](agent-wave-2026-08-25-legacy-parser-message-safety.md).

A path-text follow-up exercises valid filenames containing Unicode line and
paragraph separators, backslashes, quotes, trailing control characters, and a
literal trailing backslash. Printable path text remains exact, while
non-printable path text uses the existing escaped representation so API and CLI
diagnostics stay one-line and agree. No additional defect was reproduced;
evidence is recorded in
[`agent-wave-2026-08-25-legacy-parser-path-text.md`](agent-wave-2026-08-25-legacy-parser-path-text.md).

The probe also treats `for` targets that rebind either reported contract value
as blocked source input. Without this check, a later loop target could shadow a
previously recognized plain assignment while the report still claimed the
original formula. This remains an exact source-contract guard; it does not
import or execute the model. Evidence is recorded in
[`agent-wave-2026-08-25-legacy-loop-rebind.md`](agent-wave-2026-08-25-legacy-loop-rebind.md).

Named-expression targets (`:=`) in the declared method scope are also treated
as bindings. Without this check, a later `division_prob := ...` could overwrite
the reported local gate while the probe still accepted the earlier plain
assignment. The guard is source-level only and does not import or execute the
model. Evidence is recorded in
[`agent-wave-2026-08-25-legacy-named-expression.md`](agent-wave-2026-08-25-legacy-named-expression.md).

Assignment-target inspection only treats actual binding positions as bindings.
For example, `lookup[self.division_prob] = 0` uses the attribute as a subscript
expression, not as the assignment target, so it must not be mistaken for a
second contract assignment. Tuple/list/starred binding targets remain
recursive, while subscript values and slices are ignored. This is a
source-only AST boundary; it does not import or execute the model. Evidence is
recorded in
[`agent-wave-2026-08-25-legacy-target-reference.md`](agent-wave-2026-08-25-legacy-target-reference.md).

The probe also inventories other method-scope binding forms that could replace
the exact reported value after its formula assignment: `with`/`async with`,
`except ... as`, `async for`, import aliases, and nested function/class names.
Comprehension targets and lambda parameters/body bindings remain isolated to
their nested scopes. Assignment expressions in a method-level comprehension
still bind the containing method, while lambda defaults are evaluated in that
method and remain inspected. Evidence is recorded in
[`agent-wave-2026-08-25-legacy-binding-forms.md`](agent-wave-2026-08-25-legacy-binding-forms.md)
and [`agent-wave-2026-08-25-legacy-lambda-comprehension-scope.md`](agent-wave-2026-08-25-legacy-lambda-comprehension-scope.md).
