# ROADMAP

Living plan for the cancer-ca project. Status labels: `[ ]` open, `[x]` done.

## Now

- [ ] Publish repo as `fabianxvogt/cancer-ca` (this prep: gitignore, README, LICENSE, layout)
- [ ] Calibrate `local_division_rate` semantics (probability vs rate scale) against intended
      behavior (see `docs/README.md`)
  - [x] Add seeded untreated-trajectory regression coverage before any model change
- [x] Add a dependency-light source contract for the legacy division-gate scale.
- [x] Add a dependency-aware bounded structural smoke entry point with focused contract tests.
- [x] Verify exact installed dependency versions against `requirements.txt` in the structural smoke.
- [x] Verify every required smoke import has an exact distribution pin before environment checks.
- [x] Check direct `core_experiment.py` imports against the distribution-pin map without importing dependencies.
- [x] Add a minimal legacy-semantics smoke test and a bounded core-experiment smoke run.
- [x] Pin the verified research dependency set in `requirements.txt`.

## Next

- [ ] Add dual-metric result to main figures (controllability vs elimination metric side by side)
- [ ] Rule ablation studies (which meta-rules drive the tradeoff?)
- [ ] Widen parameter regime so correlations are not dominated by deterministic coupling
- [ ] Decide publication venue; update citation section once submitted/accepted

## Later

- [ ] Extended model: immune system, toxicity, vascular structure
- [ ] Reanalysis of public trial data with stability metrics
- [ ] Connections: cellular-automata irreducibility work in `toy-projects/rule30`,
      evolutionary-control ideas in `research/`

## Done

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
