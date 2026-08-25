# Roadmap review: dual metric, rule ablation, and calibration

**Date:** 2026-08-25
**Classification:** `INCREMENTAL` — owner decision memo and evidence boundary only.
**Scope:** Review of the three open roadmap items. No model code, manuscript claims,
generated figures, dependencies, private data, or roadmap status checkboxes were changed.

## Executive disposition

| Item | Current disposition | Safe source-contract status | Owner decision required |
| --- | --- | --- | --- |
| Dual-metric figure | Keep open; numerical evidence is incomplete and not yet comparable to the main figure. | Direct-import pin preflight is complete for `figure_S1_metric_dependence.py`. | Freeze the metric definitions, comparison window, and whether the result belongs in the main figure or supplement. |
| Rule ablation | Keep open; no ablation implementation or result exists. | The current source contains identifiable therapy-coupled branches, but the ablation manifest is not yet an approved scientific contract. | Define which rules are ablated, what “off” means, the estimand, and the paired design. |
| `local_division_rate` calibration | Keep open; current behavior is guarded but its intended meaning is unresolved. | Source contract and seeded untreated-trajectory regression are complete. | Choose Bernoulli probability, rate/propensity, or deliberate legacy eligibility score before any behavior change. |

Recommended owner disposition: do not close any of the three items from the current
evidence. Treat the completed pin checks and regression tests as guardrails, not as
scientific validation.

## Evidence baseline

- `[FORMAL]` The project source initializes `local_division_rate` to `4.0` and uses
  `0.8 * local_division_rate` in the random division comparison
  (`tumor_ca.py:45-48`, `tumor_ca.py:161-163`). The current default threshold is
  therefore `3.2`, outside the Bernoulli interval `[0, 1]`.
- `[EMPIRICAL]` The focused legacy regression preserves one six-step, 9×9 untreated
  trajectory for seed 7, same-seed replay, and different-seed divergence
  (`tests/test_legacy_untreated.py`). It does not calibrate the rate or validate a
  biological interpretation.
- `[FORMAL]` The source/metadata contracts cover the core runner and all committed
  figure scripts, including the supplementary metric-dependence script
  (`scripts/smoke_core_experiment.py`).
- `[REPORTED]` The latest dependency-light verification passed 17 focused tests, and
  `scripts/legacy_division_contract.py` reported `default_threshold: 3.2` with
  `threshold_in_unit_interval: false`.
- `[REPORTED]` The exact-parameter dual-metric probe timed out inside the model before
  producing any intensity row or correlation. No fresh numerical sign-flip evidence
  was produced by that probe (`docs/agent-wave-2026-08-25-dual-metric.md`).

## 1. Dual-metric figure

### What is safe now

The existing supplementary source is statically covered: its direct imports are
mapped to exact pins, and the source inventory includes it. This is safe
reproducibility metadata only. It does not justify adding the result to the main
figure or changing a paper claim.

### Why the numerical result is not ready for promotion

`figure_S1_metric_dependence.py` and `figure2_main_result.py` do not measure the same
experiment:

- The supplementary script runs five fixed intensities with one seed, 200 untreated
  steps, 100 therapy steps, and 100 post-therapy steps. It initializes with the
  default `normal_cells=True`.
- Its “controllability” value is a final-size reversibility proxy, not the composite
  `StabilityMetrics` score used by the main experiment.
- Its variance score is computed over the complete 200-observation history, while
  response uses only the therapy portion.
- The main experiment uses five named strategies, `normal_cells=False`, 500 steps,
  and a composite of four stability components.
- No committed `images/figureS1_metric_dependence.png` or result table exists. The
  image inventory still describes six ready figures, so the supplementary source is
  not currently a reproducible figure artifact.

The historical `+0.9558`/`-0.9995` values remain `[REPORTED]` project claims, not
fresh evidence from this lane. The variance metric may be a useful normative
comparison, but its normalization and observation window require owner approval
before interpretation.

### Evidence gate before closing the roadmap item

1. Owner freezes whether the target is the main composite versus the simplified
   proxy, and defines a common baseline, nadir window, follow-up window, and metric
   normalization.
2. Run the exact comparison as bounded, independently observable rows. Record raw
   response and metric vectors, Pearson inputs/outputs, and same-seed replay before
   creating or replacing any figure artifact.
3. Report the result as a five-point, one-seed metric-dependence demonstration unless
   an owner-approved multi-seed design supports a stronger label.
4. Only then decide whether to add a side-by-side panel to the main figure, keep it
   supplementary, or revise the claim. That decision is scientific judgment, not a
   source-contract task.

## 2. Rule-ablation studies

### Current source inventory

`AdvancedTumorCA.apply_meta_therapy_rules` contains three identifiable therapy-coupled
state updates:

| Candidate mechanism | Current implementation | Source location |
| --- | --- | --- |
| Stress-induced mutation | Multiply local mutation rate by `1.2`, capped at `0.05`. | `tumor_ca.py:116-120` |
| Growth suppression | Multiply local division rate by `0.9` under the therapy mask. | `tumor_ca.py:122-123` |
| Resistant-cell niche protection | Multiply local death sensitivity by `1 - 0.3 * resistant_density`. | `tumor_ca.py:125-136` |

Direct therapy killing in `rule_d_therapy_effect` should be treated as a common
baseline unless the owner explicitly defines it as an ablation factor. The source
also contains a “relaxation” branch for cells below the therapy threshold, but
`step()` calls `apply_meta_therapy_rules` only when some therapy is positive. Under
the full-grid schedules used by the core experiment, post-therapy relaxation is not
executed through that path. This is an implementation fact to account for, not a
license to change it in this review.

There is a documentation-model mismatch requiring judgment: the README and paper
describe hypoxia/rule relaxation as a meta-rule, while the source has nutrient
consumption, diffusion, and starvation thresholds but no explicit therapy-coupled
hypoxia-relaxation branch. The owner must decide whether this is a conceptual label,
an omitted mechanism, or an item outside the ablation scope.

### Scientific decisions required

Before implementation, freeze:

- the ablation set and whether direct therapy kill is held fixed;
- the meaning of “off” for each stateful update, including caps, cumulative niche
  protection, and any recovery behavior;
- the paired initial state, schedules, seeds, grid, and horizon;
- primary outputs (response, resistant fraction, composite stability, and/or metric
  sign) and an interaction analysis rather than only one-factor anecdotes.

A safe source-contract improvement could later check that an owner-approved ablation
manifest still names real branches. No such manifest is currently approved, so adding
one now would encode scientific judgment prematurely.

## 3. `local_division_rate` calibration

### What is safe now

The existing source contract and untreated regression are appropriate pre-change
guardrails. They preserve legacy behavior without asserting that the behavior is a
valid probability model. No model change is safe until the semantic choice is made.

### Decision required

The current decision memo correctly presents three incompatible readings:

1. Bernoulli probability: choose whether the raw or scaled value is the probability
   and keep that value in `[0,1]`.
2. Rate/propensity: retain an unbounded rate only after defining its unit and an
   explicit conversion to an event probability.
3. Legacy eligibility score: preserve the saturating gate and document that it is not
   a probability.

This is both a scientific semantics decision and a compatibility decision: a
rescaling can change seeded trajectories and every dependent result. The existing
source contract must not be weakened merely to make the default threshold look like
a probability.

### Evidence gate before changing behavior

After the owner selects a meaning, use the already documented isolated sweep of
`{0.5, 1.0, 1.25, 4.0}` to compare raw thresholds, observed gate behavior, seeded
trajectories, and replay hashes. Then explicitly decide whether legacy figures are
rebaselined, retained as legacy outputs, or retired. This is the smallest useful
calibration experiment; it still does not establish clinical validity.

## Documentation risks to resolve separately

- `docs/PAPER_OUTLINE.md` contains stronger “proof” and universal-framing language
  than the README and paper’s later model-contingency caveats. This review does not
  rewrite those claims; the owner should decide which document is authoritative before
  publication work resumes.
- `images/README.md` says all six figures are ready, while the supplementary dual-
  metric source has no committed image. This is a documentation/inventory mismatch,
  not evidence that a figure should be generated now.

## Owner decisions requested

1. Keep all three roadmap items open.
2. For the dual metric, approve a common metric/window contract and choose main
   figure versus supplement only after a completed exact run.
3. For ablation, approve the rule manifest and factorial/paired experimental design,
   including the treatment of the undocumented explicit hypoxia rule.
4. For calibration, select the operational semantics before authorizing any model
   or generated-output change.
