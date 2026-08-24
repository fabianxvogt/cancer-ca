# Dual-metric sign-flip probe (2026-08-25)

## Outcome

The exact supplementary sign-flip path was attempted in an isolated pinned
dependency overlay, but it did not finish within the bounded run. It was
interrupted during `run_simulation` before any intensity row or Pearson
correlation was emitted. This is an execution blocker, not evidence that the
sign flip reproduced or failed.

Classification: `INCREMENTAL` — bounded runtime/infrastructure finding only;
no new scientific claim is supported.

## Intended comparison

The probe imported `run_simulation` and
`compute_alternative_stability_variance` from
`figure_S1_metric_dependence.py`; it did not call `main()` and therefore did
not create the supplementary figure. The exact parameters were:

| Parameter | Value |
| --- | --- |
| intensities | `[0.15, 0.30, 0.45, 0.60, 0.75]` |
| seed | `42` |
| grid size | `120 x 120` |
| initialization | `radius=20`, `normal_cells=True` (default) |
| untreated steps | `200` |
| therapy duration | `100` steps, constant full-grid intensity |
| post-therapy steps | `100` |
| history length | `200` observations per run |

For each intensity, the harness used the source script's definitions:

```text
response = (baseline - min(total[:duration])) / baseline * 100
baseline = total[0]
controllability_proxy = 1 - min(abs(final - baseline) / (baseline + 1), 1)
variance_stability = 1 - min(var(total) / max(total)**2, 1)
```

The two requested correlations were `scipy.stats.pearsonr(response,
controllability_proxy)` and `scipy.stats.pearsonr(response,
variance_stability)`.

## Runtime and output

The base interpreter was Python `3.9.6`; SciPy, Matplotlib, pandas, and
scikit-learn were unavailable in it. The probe therefore installed the pinned
overlay from `requirements.txt`:

```text
numpy==2.0.2
scipy==1.13.1
matplotlib==3.9.4
scikit-learn==1.6.1
pandas==2.3.3
seaborn==0.13.2
```

Runtime settings were `PYTHONPATH=<temporary-overlay>:/Users/fabian/Development/apps/cancer-ca`,
`MPLBACKEND=Agg`, and a temporary `MPLCONFIGDIR`. Installation succeeded.
Matplotlib reported that it was building a temporary font cache. The probe
then remained inside `tumor_ca.py`'s proliferation loop and was interrupted
with `KeyboardInterrupt` at `rule_a_proliferation` line 163. No numerical rows,
trajectory hashes, replay result, p-values, or correlation coefficients were
produced.

## Limitations

- The sign-flip claim remains unverified by this lane; the historical values
  in the project README were not re-used as fresh probe output.
- The source's “controllability” value is a final-size proxy, not the full
  `StabilityMetrics` composite.
- The variance metric uses the complete 200-step recorded trajectory, while
  response uses only the first 100 therapy observations.
- This is one seed and five fixed intensities in a narrow, deterministic model
  regime; even a completed run would not establish robustness or clinical
  meaning.
- `tumor_ca.py`, figures, manuscript files, and generated project outputs were
  not changed. The figure entry point was never executed.

## Next experiment

Run the same five rows as five independent no-plot jobs, emitting one row
immediately after each intensity and enforcing a per-row timeout. Keep
`size=120`, `radius=20`, `untreated_steps=200`, `duration=100`,
`post_therapy_steps=100`, and `seed=42` for comparability. If a row still
exceeds the bound, first run a screening-only pilot with an explicitly reduced
grid and horizon, label it non-comparable, and do not use it to update the
main figure or manuscript. A completed exact-parameter run should report the
five response values, both metric vectors, Pearson `r`/`p`, and a same-seed
replay check before the roadmap item is treated as evidenced.
