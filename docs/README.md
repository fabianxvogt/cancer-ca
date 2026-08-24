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
