# Decision memo: `local_division_rate` semantics

**Status:** Human decision required
**Classification:** `INCREMENTAL` — documentation of an unresolved software
semantics question; no model or scientific claim is added.

This memo is a contract aid, not a recommendation. It records what the source
does, what each plausible reading would risk preserving or changing, and the
smallest experiment that should be run only after the owner selects a reading.

## Decision

Choose one operational meaning before changing `tumor_ca.py` or interpreting
new results:

1. **Bernoulli probability:** define whether `local_division_rate` itself, or
   `0.8 * local_division_rate`, is the probability. The chosen quantity must be
   in `[0, 1]`.
2. **Rate/propensity:** retain an unbounded rate such as `4.0`, but first define
   its time unit and an explicit rate-to-probability conversion.
3. **Legacy eligibility score:** preserve the current threshold behavior and
   document that this is an unbounded score whose gate saturates, not a
   probability.

The human decision is therefore both a semantic choice and a compatibility
choice: preserve the legacy behavior, or recalibrate it and accept that the
seeded trajectories and published outputs may change.

## Bounded decision matrix

The compatibility column treats the current source behavior and committed
figures/results as the baseline. “High” means that adopting the meaning as a
real probability/rate is likely to change the division mask and therefore
downstream random draws, placements, mutations, trajectories, and dependent
outputs. This is a risk assessment, not a selection.

| Candidate semantics | Static/source fit | Compatibility risk | Contract question for the owner |
| --- | --- | --- | --- |
| **Bernoulli probability** | `[FORMAL]` The comparison is written as a probability-like gate, but the default derived threshold is `3.2`, outside `[0, 1]`. If `0.8 * local_division_rate` is the probability, the raw field must be at most `1.25`. | **High** if the default is rescaled into `[0, 1]`: current eligible cells always pass, while a sub-unit probability would not. An explicit saturation rule could preserve current eligibility, but then the raw field and derived probability still need separate definitions. | Is the raw field or the scaled value the probability, and is preserving the existing gate/outputs a hard constraint? |
| **Rate/propensity** | `[FORMAL]` The field is unbounded at `4.0` and is modified multiplicatively under therapy (`* 0.9`), which is compatible with a relative rate. `[FORMAL]` No time unit, hazard, or rate-to-probability conversion is present; `0.8` is not documented as a time step. | **High/unknown** until a time unit and conversion are fixed. Any non-saturating conversion can change the current gate; different conversions can produce different trajectories even with the same seed. | What is one model step in rate units, and which explicit conversion to an event probability is authoritative? |
| **Legacy eligibility score** | `[FORMAL]` This exactly matches the implemented rule `u < 0.8 * local_division_rate`. At the default `3.2`, every eligible tumor cell passes the gate; the field remains a score, not a probability. | **Low for output preservation** if the formula and state updates remain frozen; **high for semantic debt** because all thresholds at or above `1.25` are indistinguishable at the eligibility gate and the value has no stated physical unit. | Is preserving the current formula and committed outputs more important than assigning a probability/rate interpretation? |

The source also makes the compatibility boundary stateful: therapy multiplies
the local division field by `0.9`, while the no-therapy branch applies
`min(1.01 * local_division_rate, 0.8)` (`tumor_ca.py:122-146`). The owner-approved
experiment must therefore compare the chosen meaning against the current
stateful updates, not only against the constructor default.

## Plausible meanings

| Meaning | Evidence and consequence |
| --- | --- |
| **Bernoulli probability** | `[FORMAL]` The code names the derived value `division_prob` and compares it with `np.random.random(...)` (`tumor_ca.py:162-163`). `[FORMAL]` The default raw value is `4.0`, so the derived threshold is `3.2`; that is not a valid probability. If `0.8 * rate` is intended as the probability, the raw rate must not exceed `1.25`. |
| **Rate/propensity** | `[FORMAL]` The raw value is initialized to `4.0`, is described as “high division,” and is multiplied by `0.9` under therapy (`tumor_ca.py:47, 122-123`). `[SPECULATIVE]` This could be a relative rate, but the code defines no time unit, hazard, or conversion such as a bounded event probability. The constant `0.8` is not evidence of a time step. |
| **Legacy eligibility score** | `[FORMAL]` The implemented rule is exactly `u < 0.8 * local_division_rate` for cells already meeting nutrient and empty-neighbor conditions. With the default threshold `3.2`, every such tumor cell passes the division gate because `u` is drawn from `[0, 1)`. Placement and later mutation remain stochastic. This is the strongest statement about current behavior, not a claim that the score is scientifically appropriate. |

## What the current code and tests establish

- `[FORMAL]` `local_division_rate` is a per-cell array initialized to `4.0`
  (`tumor_ca.py:45-48`). Tumor proliferation additionally requires at least
  one empty neighbor and nutrient level above `0.3`
  (`tumor_ca.py:154-163`). Normal-cell proliferation uses a separate fixed
  `0.1` gate (`tumor_ca.py:187-193`).
- `[FORMAL]` The source contract reports raw rate `4.0`, scale `0.8`, derived
  threshold `3.2`, and `threshold_in_unit_interval == False`. It intentionally
  rejects a clamped or non-multiplicative replacement
  (`scripts/legacy_division_contract.py:51-67`,
  `tests/test_legacy_semantics.py:8-27`).
- `[EMPIRICAL]` The untreated regression pins one six-step, 9×9 setup at
  seed `7` to total-tumor counts `(10, 20, 33, 50, 70, 80)`, a final-grid
  fingerprint, same-seed replay, and different-seed divergence
  (`tests/test_legacy_untreated.py:11-44`).
- `[EMPIRICAL]` Those tests do not sweep the parameter, estimate gate
  frequencies, define rate units, or establish that `3.2` is a valid
  probability. They also do not establish a biological or medical result.
- `[REPORTED]` The README, docs index, and roadmap already record the scale
  mismatch as deferred calibration work and leave the model unchanged.

## Smallest owner-approved falsification experiment

No run is authorized by this memo alone. Before execution, the owner must name
one matrix row, state whether the existing seed-7 fingerprint and committed
outputs are a preservation requirement, and approve an isolated comparison
harness. The harness must not edit `tumor_ca.py`, regenerate figures, update
JSON results, or change dependencies.

Once approved, use the exact pins in [`requirements.txt`](../requirements.txt)
and `MPLBACKEND=Agg`:

1. Evaluate the unchanged gate at only
   `local_division_rate = {0.5, 1.0, 1.25, 4.0}`, recording the raw thresholds
   `{0.4, 0.8, 1.0, 3.2}` and the observed pass fraction for fresh uniform
   draws. This is the dependency-light discriminator for the unit-interval
   and saturation claims.
2. For those same four values, use the existing `size=9`, `seed=7`,
   `radius=1`, `normal_cells=False`, untreated six-step setup. Record only the
   six `total_tumor` values, final-grid SHA-256, and a same-seed replay check.
3. Compare the observations to the owner-selected row and preservation rule.
   Use seed `8` only if the owner wants the existing different-seed guard
   repeated; it is not needed to discriminate the three semantics.

**Falsification rule:** a probability reading is falsified if its declared
probability does not match the measured gate fraction or leaves the unit
interval. A rate reading is falsified as an implementation description if it
expects distinct rates above the saturation boundary to remain distinguishable
but `1.25` and `4.0` produce the same gate and seeded trajectory. A legacy-score
reading is supported only by observing that saturation and reproducing the
existing seed-7 regression; that support does not validate the model’s
scientific interpretation.

The experiment is intentionally a compatibility probe, not a calibration of a
biological parameter. Its result must be reviewed by the owner before any
semantic change, figure regeneration, or interpretation of new model outputs.
