# AI-owned project documentation

Use this folder for concise, reviewable notes maintained by coding agents: verified setup, architecture, validation commands, and bounded cleanup plans.

The project README and any document marked `human-owned` remain authoritative. Do not overwrite human-owned material or make unsupported claims.

Never store credentials, private data, generated output, logs, datasets, or build artifacts here. Preserve unrelated local work and keep each change focused.

## Deferred calibration finding

The local research scripts currently expose a scale mismatch: `local_division_rate` is used as a probability-like threshold, but the observed calculation is not guaranteed to remain in the unit interval. Untreated trajectories also use deterministic choices, so changing that scale or introducing stochastic behavior could alter existing results and published figures.

This is a documented follow-up, not a behavior change. Before changing the model, calibrate the scale against the intended probability semantics, add regression coverage for untreated trajectories, and compare representative outputs. Do not modify the pre-existing untracked `tumor_ca.py` or research artifacts as part of this note.

### Guardrail for interpretation

`local_division_rate` is a raw multiplier used as a probability-like threshold: the current gate compares a random draw with `0.8 * local_division_rate`. The default `4.0` therefore yields `3.2`, making the division gate deterministically eligible when nutrient and empty-neighbor conditions also pass. Later mutation, placement, and death steps remain stochastic. This documents legacy behavior for reproducibility; it does not claim structural robustness or justify rescaling the model.

## Focused regression check

Run `python3 -m pytest -q tests/test_legacy_semantics.py` before changing the
division-rate scale. The test intentionally captures the current default gate;
calibration work should replace it only after comparing untreated trajectories.

The bounded core smoke used the versions pinned in [`../requirements.txt`](../requirements.txt).
It validates importability and branch execution on a small grid, not the
scientific conclusions of the full experiment.

The reusable command is `python3 scripts/smoke_core_experiment.py`; its output
and empirical limits are recorded in
[`agent-wave-2026-08-25-structural-smoke.md`](agent-wave-2026-08-25-structural-smoke.md).
The command also verifies that installed distribution versions exactly match
`requirements.txt`; this is an environment contract, not a claim that the model
is scientifically validated.

## Calibration contract probe

Run `python3 scripts/legacy_division_contract.py` to inspect the legacy division
gate without importing dependencies or executing the model. The focused test
keeps the raw default multiplier, gate scale, and derived threshold explicit;
it is a pre-change guardrail for calibration, not a probability calibration or
scientific validation.
