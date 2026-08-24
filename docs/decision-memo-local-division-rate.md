# Decision memo: `local_division_rate` semantics

**Status:** Human decision required
**Classification:** `INCREMENTAL` — documentation of an unresolved software
semantics question; no model or scientific claim is added.

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

## Smallest dependency-backed falsification experiment

Run only after the human selects the intended probability/rate mapping. Use an
isolated harness with the exact pins in [`requirements.txt`](../requirements.txt)
and `MPLBACKEND=Agg`; do not edit `tumor_ca.py`.

1. Import `AdvancedTumorCA`, create the existing `size=9`, `seed=7`,
   `radius=1`, `normal_cells=False`, untreated setup, and keep nutrients at a
   value above `theta_div`.
2. Sweep only `local_division_rate` values `{0.5, 1.0, 1.25, 4.0}`. For the
   fixed initially eligible tumor cells, estimate the gate-pass fraction over
   repeated fresh draws using the exact current expression and record the raw
   thresholds `{0.4, 0.8, 1.0, 3.2}`.
3. For each value, run the existing six-step setup once and record the six
   `total_tumor` values and final-grid SHA-256. Replay seed `7`; use seed `8`
   only for the already-established different-seed check.

**Falsification rule:** a probability reading is falsified if its declared
probability does not match the measured gate fraction or leaves the unit
interval. A rate reading is falsified as an implementation description if it
expects distinct rates above the saturation boundary to remain distinguishable
but `1.25` and `4.0` produce the same gate and seeded trajectory. A legacy-score
reading is supported only by observing that saturation and reproducing the
existing seed-7 regression; that support does not validate the model’s
scientific interpretation.
