# ROADMAP

Living plan for the cancer-ca project. Status labels: `[ ]` open, `[x]` done.

Current owner review (all three items remain open): [dual-metric, rule-ablation, and calibration disposition](docs/roadmap-review-2026-08-25.md).

## Now

- [x] Publish repo as `fabianxvogt/cancer-ca` (published 2026-08-22; public
  remote and push-clean state verified)
- [ ] Calibrate `local_division_rate` semantics (probability vs rate scale) against intended
      behavior (see `docs/README.md`)
  - [x] Add seeded untreated-trajectory regression coverage before any model change
  - [x] Add a dependency-light source contract for the legacy division-gate scale.
  - [x] Expand the contract probe to report the memo's four thresholds, saturation,
        and unset owner decision boundary without model execution.
  - [x] Record the three-way semantics/compatibility matrix and owner-gated
        bounded experiment; semantic choice remains open.
- [x] Add a dependency-aware bounded structural smoke entry point with focused contract tests.
- [x] Verify exact installed dependency versions against `requirements.txt` in the structural smoke.
- [x] Verify every required smoke import has an exact distribution pin before environment checks.
- [x] Check direct `core_experiment.py` imports against the distribution-pin map without importing dependencies.
- [x] Check all committed `figure*.py` imports against the distribution-pin map without importing dependencies.
- [x] Guard the figure-source pin contract with an explicit inventory matching the figure map.
- [x] Guard manuscript cross-references against undefined LaTeX labels.
- [x] Guard manuscript image paths and supplementary figure inclusions against
      the committed image inventory.
- [x] Add a minimal legacy-semantics smoke test and a bounded core-experiment smoke run.
- [x] Pin the verified research dependency set in `requirements.txt`.
- [x] Keep invalid legacy-contract CLI paths explicit and non-tracebacking;
      this validates the evidence probe only and does not alter model semantics.
- [x] Keep non-UTF-8 legacy-contract source inputs explicit and non-tracebacking;
      this hardens parsing boundaries only and does not alter model semantics.
- [x] Reject duplicate legacy-contract assignments instead of silently selecting
      the first AST match; this hardens evidence parsing only and does not alter
      model semantics.
- [x] Require the legacy-contract assignments to use their declared method
      scopes and exact target shapes; this blocks same-name decoys and malformed
      assignments without altering model semantics.
- [x] Return an isolated owner-decision payload from the legacy contract probe;
      repeated reports remain deterministic if a caller mutates one result.
- [x] Reject a zero legacy gate multiplier before saturation-boundary division;
      invalid source contracts remain explicit API errors and CLI blocks.
- [x] Reject finite constants whose derived legacy-contract thresholds or
      saturation boundary overflow to non-finite report values.
- [x] Convert oversized integer multiplier literals into explicit blocked
      contract results instead of leaking float-conversion tracebacks.
- [x] Escape non-printable legacy-contract source paths in API/CLI errors so
      blocked messages remain deterministic and line-safe.
- [x] Preserve exact source filenames and parser locations in API/CLI errors;
      normalize syntax and embedded-NUL parser failures to the established
      `ValueError`/status-2 contract.
- [x] Audit parser diagnostics across CRLF, mixed multiline source, and
      repeated embedded-NUL fixtures; no additional API/CLI defect was
      reproduced, and the deterministic line-safe boundary is regression-tested.
- [x] Audit unusual parser messages and source control characters, including
      malformed strings/f-strings, mismatched delimiters, C0 controls, and
      Unicode line separators; no additional API/CLI defect was reproduced,
      and the one-line diagnostic boundary is regression-tested.
- [x] Audit parser diagnostics for unusual valid filesystem path text,
      including Unicode separators, backslashes, quotes, trailing controls,
      and a literal trailing backslash; no additional API/CLI defect was
      reproduced, and exact API/CLI path-display parity is regression-tested.
- [x] Reject loop-target rebindings of legacy-contract values instead of
      silently accepting a later shadowing source assignment.
- [x] Reject named-expression rebindings of legacy-contract values instead of
      silently accepting a later `:=` shadowing source assignment.
- [x] Distinguish binding positions from nested target expressions so attribute
      references inside subscript targets do not create false duplicate matches;
      tuple/list/starred rebindings remain blocked.
- [x] Reject remaining method-scope binding forms (`with`/`except` aliases,
      async loops, import aliases, and nested function/class names) instead of
      silently accepting a later shadowing source construct.
- [x] Distinguish nested lambda/comprehension scopes from method scope: ignore
      lambda-body and comprehension-target bindings, retain method-scope
      comprehension assignment expressions, and inspect lambda defaults.

## Next

- [ ] Add dual-metric result to main figures (controllability vs elimination metric side by side)
  - [x] Add metadata-only direct-import pin preflight for the existing supplementary figure.
- [ ] Rule ablation studies (which meta-rules drive the tradeoff?)
- [ ] Widen parameter regime so correlations are not dominated by deterministic coupling
- [ ] Decide publication venue; update citation section once submitted/accepted

## Later

- [ ] Extended model: immune system, toxicity, vascular structure
- [ ] Reanalysis of public trial data with stability metrics
- [ ] Connections: cellular-automata irreducibility work in `toy-projects/rule30`,
      evolutionary-control ideas in `research/`

## Done

- [x] 2026-08-25: added a self-checking 24-execution, three-seed Adaptive
      semantics × cutoff factorial with cross-yoked dose paths. Its 16 unique
      tumor trajectories and four unique dose paths include eight exact replay
      checks. Under the capacity-scaled all-high path, bounded pretherapy
      response contrasts persist but change sign by seed, so no directional
      claim is supported. [INCREMENTAL / EMPIRICAL bounded software-model
      audit]
- [x] 2026-08-25: added a self-checking fixed-seed division-semantics
      sensitivity audit without changing model behavior. The documented `1.0`
      counterfactual changes 44.4%–56.6% of final cells while preserving
      response/burden ranks and swapping one stability-rank pair. Exact result
      and full-trajectory replay fingerprints are enforced; the reduced
      Adaptive arm's unscaled cutoff and changed dose exposure are documented.
      Calibration remains an open owner decision. [INCREMENTAL / EMPIRICAL
      bounded audit]
- [x] Core model (`tumor_ca.py`) + stability metrics framework
- [x] Core experiment: 5 strategies, response-vs-stability correlation
- [x] Statistical validation: bootstrap CIs, 20-seed reproducibility, metric sign-flip discovery
- [x] Full paper draft (`paper.tex`, 11 pp.) compiling with all 6 figures + supplement
- [x] Reviewer response round: overclaiming language removed, metric circularity acknowledged
- [x] Publication prep: .gitignore, publication README, LICENSE (MIT), scratch/ organization
- [x] 2026-08-24: added a focused regression test for the current default division-gate
      semantics without changing the model implementation.
- [x] 2026-08-25: pinned the dependency overlay used by the bounded core smoke;
      full scientific claims remain outside the smoke's scope.
- [x] 2026-08-25: added metadata-only coverage for required smoke-import pins;
      this does not imply scientific comparability.
- [x] 2026-08-25: reconciled an undefined manuscript figure reference with the
      existing phase-boundaries table; no figures were regenerated.
- [x] 2026-08-25: reconciled committed supplementary Figures S2–S4 with their
      manuscript image inclusions and added a dependency-free asset contract.
- [x] 2026-08-25: reconciled the publication checkbox with the root portfolio
      record and verified the public remote/push-clean state.
- [x] 2026-08-25: made non-UTF-8 legacy-contract inputs return an explicit
      blocked result instead of leaking a decoding traceback.
- [x] 2026-08-25: isolated mutable owner-decision metadata from returned legacy
      contract reports; this hardens reproducibility without changing semantics.
- [x] 2026-08-25: rejected zero legacy gate multipliers before computing the
      saturation boundary, preventing an uncaught division-by-zero traceback.
- [x] 2026-08-25: rejected non-finite derived contract values so finite source
      constants cannot leak `Infinity` into the JSON evidence report.
- [x] 2026-08-25: converted oversized integer multiplier literals into the
      established API `ValueError` and CLI status-2 boundary.
- [x] 2026-08-25: escaped non-printable legacy-contract source paths in blocked
      API/CLI errors so parser and file errors remain line-safe.
- [x] 2026-08-25: preserved exact source paths and parser locations for syntax
      and embedded-NUL failures, keeping the API/CLI error boundary explicit.
- [x] 2026-08-25: audited CRLF, mixed multiline source, and repeated embedded
      NUL diagnostics; no runtime change was warranted after API/CLI checks.
- [x] 2026-08-25: audited unusual `SyntaxError` messages and raw source control
      characters; no runtime change was warranted because the wrapper excludes
      `SyntaxError.text` and keeps API/CLI diagnostics line-safe.
- [x] 2026-08-25: audited valid filesystem path text containing Unicode
      separators, backslashes, quotes, trailing controls, and a trailing
      backslash; no runtime change was warranted because API/CLI diagnostics
      already preserve printable text and escape non-printable text line-safely.
- [x] 2026-08-25: rejected loop-target rebindings of legacy-contract values so
      exact source reports cannot ignore a later shadowing binding.
- [x] 2026-08-25: rejected named-expression rebindings of legacy-contract values
      so exact source reports cannot ignore a later `:=` shadowing binding.
- [x] 2026-08-25: limited legacy-contract target inspection to actual binding
      positions, avoiding false rejection of attribute references inside
      subscript targets while preserving nested unpacking checks.
- [x] 2026-08-25: rejected method-scope `with`/`except` aliases, async-loop
      targets, import aliases, and nested function/class names so the source
      contract cannot ignore later shadowing binders.
- [x] 2026-08-25: excluded lambda-body and comprehension-target bindings from
      method-scope rebinding detection while retaining method-scope assignment
      expressions in comprehensions and lambda defaults.
