# ROADMAP

Living plan for the cancer-ca project. Status labels: `[ ]` open, `[x]` done.

## Now

- [ ] Publish repo as `fabianxvogt/cancer-ca` (this prep: gitignore, README, LICENSE, layout)
- [ ] Calibrate `local_division_rate` semantics (probability vs rate scale) against intended
      behavior; add regression coverage for untreated trajectories before any model change
      (see `docs/README.md`)
- [ ] Pin/verify dependency versions; add a minimal smoke test that runs
      `core_experiment.py` on a small grid

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
