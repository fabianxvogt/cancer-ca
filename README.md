# cancer-ca

**A cellular-automaton study of the tradeoff between tumor response and intervention stability**

Research code and manuscript for a minimal meta-cellular-automaton model in which cancer
therapy acts as a *rule operator* — it does not just kill cells, it changes mutation rates,
selection pressures, and niche structure of the evolving system.

> **Status:** research code accompanying a full paper draft (`paper.tex` / `paper.pdf`).
> This is a conceptual/modeling contribution, **not** a clinical tool. See
> [Disclaimer](#disclaimer).

---

## What it is

A 5-state cellular automaton (empty, normal, tumor-sensitive, tumor-resistant, necrotic)
on a nutrient/therapy field with local Moore-neighborhood rules, plus "meta-rules":
stress raises the mutation rate, necrosis creates protected niches, hypoxia relaxes
constraints. On top of this, five therapy strategies are compared:

| Strategy | Intensity | Duration |
| --- | --- | --- |
| MTD (maximum tolerated dose) | aggressive | short |
| Moderate continuous | medium | long |
| Intermittent | cycled | with breaks |
| Adaptive | low, responsive | long |
| Metronomic | very low | very long |

The core question: **is there a systematic relationship between how much a therapy shrinks
the tumor (response) and how long the system stays controllable afterwards (intervention
stability)?** Stability is measured by four metrics: regime stability, entropy trajectory,
reversibility loss, and control horizon.

## Why it is interesting

Most therapy optimization treats the tumor as a static target. This model makes the
evolutionary coupling explicit: therapy intensity drives both the response axis and the
stability axis through the same parameter, so the two are structurally entangled.
The paper's contribution is not a clinical claim but a formalization of the
**value tradeoff between elimination ("cure") and long-term control** — including an
explicit analysis of how the answer flips depending on which stability metric you choose.

## Key findings

All numbers below are **EMPIRICAL** results from `statistical_validation.py` within this
model class (deterministic coupling, narrow parameter regime; see paper abstract for scope):

- Near-perfect negative correlation between response and controllability-based stability:
  ρ = −0.9995, 95% CI [−0.9999, −0.9992]. Reproduced across 20/20 seeds,
  mean ρ = −0.9998 ± 0.0003.
- **Metric dependence (the honest caveat):** using an elimination-prioritizing metric
  (population-variance stability) instead flips the sign to ρ = +0.9558. The result is
  therefore framed as a *normative tradeoff*, not a universal law — the paper states this
  explicitly rather than hiding it.
- MTD achieves ~96% tumor reduction but the worst controllability score (~0.38);
  metronomic dosing achieves only ~28% reduction but the best (~0.53).
- Global parameter-space sweep: ρ = −0.96 across the sampled space
  (`figure6_parameter_space.py`).

## Repository layout

```
cancer-ca/
├── tumor_ca.py                  # Core model: AdvancedTumorCA (CA + meta-rules + analytics)
├── stability_metrics.py         # The four intervention-stability metrics
├── core_experiment.py           # Main experiment: 5 strategies, response vs stability
├── statistical_validation.py    # Correlations, bootstrap CI, seed reproducibility, sign-flip test
├── parameter_sensitivity.py     # Parameter sensitivity analysis
├── reversibility_test.py        # Reversibility metric validation
├── robustness_analysis.py       # Seed / grid-size / intensity robustness
├── deep_analysis.py             # Extended analysis suite
├── research_analysis.py         # Wolfram classification, Lyapunov-like divergence
├── figure1..6_*.py              # One standalone script per main figure -> images/
├── figure_S1_metric_dependence.py  # Supplementary: alternative-metric sign flip
├── generate_all_figures.py      # Runs all figure scripts in sequence
├── eval_figure*.py              # Figure evaluation helpers
├── images/                      # Generated figures (PNG/PDF) + result JSONs
├── docs/                        # Paper outline, agent notes
├── scratch/                     # Debug/test scripts and superseded working docs (kept, not needed to reproduce)
├── paper.tex / paper.pdf        # Full manuscript draft
└── ROADMAP.md                   # Living project plan
```

## Reproducing

Requirements (Python 3.9+, pinned for reproducible research runs):

```bash
pip install -r requirements.txt
```

```bash
python3 scripts/smoke_core_experiment.py  # bounded structural smoke; no scientific claim
python3 scripts/legacy_division_contract.py  # report legacy calibration semantics; no model run
python tumor_ca.py                 # basic simulation + emergence demo
python core_experiment.py          # the 5-strategy response-vs-stability experiment
python statistical_validation.py   # correlations, CIs, seed reproducibility, sign flip
python generate_all_figures.py     # regenerates all figures into images/
pdflatex paper.tex && pdflatex paper.tex   # rebuilds paper.pdf from images/
```

The smoke command checks dependency availability, exact installed versions against
`requirements.txt`, strategy-branch execution, and history shape at `size=32`,
`steps=205`, `seed=42`. Its JSON summary includes the verified pins. It is
intentionally a dependency-aware import/structure check: it does not reproduce
the paper's metrics, correlations, or biological conclusions. If a dependency is
missing or its version drifts, the command exits without importing the research
runner and points to the pinned `requirements.txt` environment.

The division-contract command reads `tumor_ca.py` as source and reports the
legacy raw multiplier, gate scale, and derived threshold before any calibration
change. It does not import the model, run a trajectory, or validate a scientific
result.

Figure ↔ script map:

| Figure | Script |
| --- | --- |
| Fig. 1 concept schematic | `figure1_concept.py` |
| Fig. 2 main result (ρ) | `figure2_main_result.py` |
| Fig. 3 temporal dynamics (MTD vs metronomic) | `figure3_temporal_dynamics.py` |
| Fig. 4 spatial evolutionary regime shift | `figure4_spatial_evolution.py` |
| Fig. 5 seed/size/intensity robustness | `figure5_robustness.py` |
| Fig. 6 global parameter space | `figure6_parameter_space.py` |
| S1 metric dependence (sign flip) | `figure_S1_metric_dependence.py` |

All committed figures in `images/` were generated by these scripts; result JSONs next to
them record the underlying numbers.

## Paper & citation

A full manuscript draft is included: [`paper.tex`](paper.tex) /
[`paper.pdf`](paper.pdf) — *"Intervention Stability over Response: A Tradeoff Between Cure
and Control in Recursively Coupled Evolutionary Systems"* (draft, January 2026, not yet
peer-reviewed). If you build on this work, please cite the repository until a citable
version exists.

## Known limitations

- Documented scale-mismatch risk in the division-rate parameter semantics
  (see `docs/README.md`) — calibration follow-up planned before any behavior change.
- No immune system, toxicity, or vascular structure; narrow parameter regime;
  perfect correlations reflect deterministic coupling, not stochastic robustness.

## Disclaimer

Theoretical/modeling work only. Do **not** use for clinical decisions, patient counseling,
or treatment planning.

## License

MIT — see [LICENSE](LICENSE).
