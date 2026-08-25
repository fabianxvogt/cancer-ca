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
