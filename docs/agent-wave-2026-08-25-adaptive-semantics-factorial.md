# Adaptive semantics × cutoff factorial audit

## Result

A paired three-seed, 24-execution software-model audit separates the
division-rate screen (`4.0` legacy versus `1.0` unit interval), the Adaptive
cutoff (`500` cells versus capacity-scaled `20`), and the dose path generated
downstream by the controller. It executes 12 closed-loop cells and 12
cross-yoked replays. Those executions contain 16 unique tumor trajectories and
four unique dose paths; eight cross-yoked executions exactly replay their
matching target-semantics closed-loop trajectory and serve as replay checks,
not additional intervention contrasts.

**EMPIRICAL:** capacity scaling makes all six reduced-grid paths continuous
full dose: 100 high-dose steps and cumulative exposure `25.0`. Despite this
common dose path, unit-minus-legacy response contrasts from the last untreated
state are `-2.946274`, `+12.651646`, and `+0.519931` percentage points for seeds
41–43. The inherited metric, whose baseline is the state after the first active
dose, gives `-2.982456`, `+12.902857`, and `+0.355481`. These are strictly
bounded contrasts between simulated trajectories under one shared dose path;
they do not identify why the trajectories differ. Their direction also changes
across three seeds, so no stable directional claim is supported.

For the unscaled seed-42 arm from the earlier audit, the total response contrast
from the last untreated state is `+14.038128` points. Holding the legacy dose
path fixed gives `+14.384749`; substituting the unit-generated path under unit
semantics contributes `-0.346620`. For comparison, the inherited
post-first-dose metric gives `+14.320590`, `+14.672083`, and `-0.351494` for the
same three quantities. Each decomposition is only an order-dependent arithmetic
contrast over these recorded executions and does not identify an intervention
mechanism.

Classification: **INCREMENTAL / EMPIRICAL bounded software-model audit**. No
biological, treatment, medical, or clinical claim is made.

## Reproduction

From the project root:

```bash
MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
uv run --no-project --isolated \
  --python 3.12 \
  --with 'numpy==2.0.2' --with 'scipy==1.13.1' \
  --with 'matplotlib==3.9.4' --with 'scikit-learn==1.6.1' \
  --with 'pandas==2.3.3' \
  python scripts/adaptive_semantics_factorial.py
```

The fixture was tested with Python 3.12 and the exact package versions above.
Its self-checking JSON has SHA-256
`78bbd91d190f87c73c9571faeb1eaef05b0a1bb09666358394ae625e21fc12a8`.
It emits all 12 closed-loop and 12 cross-yoked executions, complete 180-step
dose vectors and hashes, both response baselines, seed-level
burden/AUC/resistance/stability components, total-tumor trajectory hashes, both
decomposition orders, and the unique/replay counts. It fails if timing, dose
windows, named yokes, execution counts, replay counts, scaled common paths,
response formulas, or accounting identities drift.

## Interpretation and limits

The cutoff `20` exactly preserves only the source controller's capacity fraction:
`500 / 120² = 20 / 24²`. It does not make the reduced radius, horizon, schedule,
or geometry scale-equivalent to the 120×120 core experiment. Both `0.125` and
`0.25` exceed `theta_kill`, so all 100 active steps invoke the same
intensity-independent `local_division_rate *= 0.9` update; cutoff differences
act through dose-dependent cell effects, not through the count of meta-rule
updates.

Three paired seeds are a sensitivity screen, not an inferential sample. The
yoked paths can be off-policy under the target semantics, and pseudorandom draws
diverge after state trajectories separate. The capacity-scaled controller is
degenerate (always high dose), making it a bounded common-dose-path comparison
rather than evidence about responsive Adaptive therapy.
