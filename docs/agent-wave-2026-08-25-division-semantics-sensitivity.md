# Division-semantics sensitivity audit

## Result

A bounded fixed-seed counterfactual compares the unchanged legacy initial raw
division rate `4.0` (initial derived gate threshold `3.2`) with the documented
unit-interval screen `1.0` (initial threshold `0.8`). It preserves the model's
stateful therapy update, which multiplies the local rate by `0.9` before each
treated proliferation step. It does not change `tumor_ca.py` or select an
owner-approved model semantics.

Across the five declared strategies, the alternative changes 44.4%–56.6% of
the final 24×24 grid cells. Response and final-tumor-burden rankings remain
identical (`Spearman rho = 1.0`, `Kendall tau = 1.0`), while the middle two
composite-stability ranks swap (`rho = 0.9`, `tau = 0.8`). Same-seed MTD replays
have identical summary rows, final grids, and normalized hashes over all 180
per-step grids within each semantics.

Classification: **INCREMENTAL / EMPIRICAL bounded sensitivity audit**. This is
not a biological calibration, clinical result, or replacement for the paper's
120×120, 500-step experiment.

## Reproduction

Run from the project root with the exact dependency overlay:

```bash
MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
uv run --no-project --isolated \
  --with 'numpy==2.0.2' --with 'scipy==1.13.1' \
  --with 'matplotlib==3.9.4' --with 'scikit-learn==1.6.1' \
  --with 'pandas==2.3.3' \
  python scripts/division_semantics_sensitivity.py
```

The script runs both semantics at `size=24`, `steps=180`, `seed=42`, tumor
radius 5, and therapy start 25. Strategy durations are reduced to 40, 75,
three cycles of 20-on/25-off, 100, and 125 steps. It emits deterministic JSON,
validates both complete MTD trajectory sentinels, and fails explicitly if the
exact fixed-seed result fingerprint, named rankings, grid-change counts, legacy
constructor contract, or all-ones control horizons are not reproduced. The
dependency versions are pinned above, but Python, `uv`, and hardware are not;
the recorded result is a direct-dependency overlay rather than a portable
bit-for-bit environment specification.

## Interpretation and boundary

The preserved response/burden ordering suggests that this one reduced fixture's
coarse treatment ranking is less sensitive than its spatial state. The swapped
stability ranks and large cell-level differences show that the semantics are
not interchangeable for derived dynamics or every metric.

Only one seed, grid, and reduced schedule are tested. In particular, the
Adaptive arm preserves the source's absolute `tumor > 500` cutoff: that is 86.8%
of this 24×24 grid, versus 3.47% of the 120×120 core grid. This bespoke
closed-loop fixture is control-flow faithful, not scale-equivalent to the core
adaptive experiment. Its changed trajectories also change dose exposure: the
legacy arm spends 14 steps at `0.25` and 86 at `0.125`, while the unit-interval
screen spends 12 and 88 steps, respectively. These exposure counts are emitted
in the JSON.

All control horizons are 1 in this fixture, and the `1.0` value is a documented
screening candidate, not a fitted parameter. Keep the legacy rule as the
compatibility baseline until the owner chooses an operational meaning and
approves multi-seed rebaselining.
