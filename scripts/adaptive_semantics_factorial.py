#!/usr/bin/env python3
"""Paired division-semantics × Adaptive-cutoff audit with dose-path yoking."""

from __future__ import annotations

from collections.abc import Callable
from hashlib import sha256
import json

import numpy as np

from scripts.division_semantics_sensitivity import _canonical_digest, _require
from stability_metrics import ResponseVsStability, StabilityMetrics
from tumor_ca import AdvancedTumorCA


SIZE = 24
STEPS = 180
THERAPY_START = 25
THERAPY_END = 125
PRETHERAPY_BASELINE_INDEX = THERAPY_START - 1
POST_FIRST_DOSE_BASELINE_INDEX = THERAPY_START
RESPONSE_NADIR_STOP_EXCLUSIVE = THERAPY_END + 20
SEEDS = (41, 42, 43)
SEMANTICS = {"legacy": 4.0, "unit_interval": 1.0}
CUTOFFS = {"unscaled": 500, "capacity_scaled": 20}
LOW_DOSE = 0.125
HIGH_DOSE = 0.25
EXPECTED_FIXTURE_SHA256 = (
    "78bbd91d190f87c73c9571faeb1eaef05b0a1bb09666358394ae625e21fc12a8"
)
EXPECTED_HIGH_DOSE_STEPS = {
    "41:legacy:unscaled": 12,
    "41:unit_interval:unscaled": 12,
    "42:legacy:unscaled": 14,
    "42:unit_interval:unscaled": 12,
    "43:legacy:unscaled": 12,
    "43:unit_interval:unscaled": 11,
    **{
        f"{seed}:{semantic}:capacity_scaled": 100
        for seed in SEEDS
        for semantic in SEMANTICS
    },
}


def _dose_bytes(doses: tuple[float, ...]) -> bytes:
    return np.asarray(doses, dtype="<f8").tobytes(order="C")


def _trajectory_bytes(values: list[int]) -> bytes:
    return np.asarray(values, dtype="<i8").tobytes(order="C")


def _grid_bytes(grid: np.ndarray) -> bytes:
    return np.asarray(grid, dtype=np.uint8).tobytes(order="C")


def _stability_payload(metrics: dict) -> dict:
    return {
        "regime_changes": [int(value) for value in metrics["regime_changes"]],
        "stability_duration": int(metrics["stability_duration"]),
        "entropy_increase_rate": float(metrics["entropy_increase_rate"]),
        "final_entropy": float(metrics["final_entropy"]),
        "reversibility_score": float(metrics["reversibility_score"]),
        "control_horizon": int(metrics["control_horizon"]),
        "stability_score": float(metrics["stability_score"]),
    }


def _response_payload(history: dict) -> dict:
    total_tumor = np.asarray(history["sensitive"]) + np.asarray(history["resistant"])
    inherited = ResponseVsStability.measure_response(
        history, THERAPY_START, THERAPY_END
    )
    pretherapy_baseline = int(total_tumor[PRETHERAPY_BASELINE_INDEX])
    post_first_dose_baseline = int(total_tumor[POST_FIRST_DOSE_BASELINE_INDEX])
    nadir = int(np.min(total_tumor[THERAPY_START:RESPONSE_NADIR_STOP_EXCLUSIVE]))
    _require(
        int(inherited["nadir"]) == nadir,
        "inherited response nadir window drifted",
    )
    return {
        "response_pretherapy_pct": float(
            (pretherapy_baseline - nadir) / (pretherapy_baseline + 1) * 100
        ),
        "response_inherited_post_first_dose_pct": float(inherited["max_reduction"]),
        "pretherapy_baseline_tumor": pretherapy_baseline,
        "post_first_dose_baseline_tumor": post_first_dose_baseline,
        "final_tumor_burden": int(inherited["final_tumor_burden"]),
        "nadir": nadir,
    }


def _validate_dose_window(key: str, row: dict) -> None:
    doses = row["dose_path"]
    active_path = doses[THERAPY_START:THERAPY_END]
    _require(len(doses) == STEPS, f"dose path length drifted for {key}")
    _require(
        all(dose == 0.0 for dose in doses[:THERAPY_START]),
        f"pre-therapy dose window drifted for {key}",
    )
    _require(
        all(dose == 0.0 for dose in doses[THERAPY_END:]),
        f"post-therapy dose window drifted for {key}",
    )
    _require(
        all(dose in (LOW_DOSE, HIGH_DOSE) for dose in active_path),
        f"active dose values drifted for {key}",
    )
    _require(
        row["high_dose_steps"] + row["low_dose_steps"] == THERAPY_END - THERAPY_START,
        f"active dose count drifted for {key}",
    )


def _run(
    seed: int,
    raw_division_rate: float,
    dose_at_step: Callable[[AdvancedTumorCA, int], float],
) -> dict:
    ca = AdvancedTumorCA(size=SIZE, seed=seed)
    ca.initialize_tumor(radius=5, normal_cells=False)
    _require(
        bool(np.all(ca.local_division_rate == 4.0)),
        "AdvancedTumorCA constructor no longer initializes the legacy 4.0 rate",
    )
    ca.local_division_rate.fill(raw_division_rate)

    doses: list[float] = []
    for step in range(STEPS):
        dose = float(dose_at_step(ca, step))
        ca.therapy = np.full((SIZE, SIZE), dose)
        doses.append(dose)
        ca.step()

    dose_path = tuple(doses)
    active_path = dose_path[THERAPY_START:THERAPY_END]
    switches = [
        THERAPY_START + index
        for index in range(1, len(active_path))
        if active_path[index] != active_path[index - 1]
    ]
    total_tumor = [int(value) for value in ca.history["total_tumor"]]
    response = _response_payload(ca.history)
    stability = StabilityMetrics.compute_all_metrics(
        ca.history, THERAPY_START, THERAPY_END
    )
    return {
        "dose_path": list(dose_path),
        "dose_sha256": sha256(_dose_bytes(dose_path)).hexdigest(),
        "high_dose_steps": sum(dose == HIGH_DOSE for dose in active_path),
        "low_dose_steps": sum(dose == LOW_DOSE for dose in active_path),
        "switch_steps": switches,
        "cumulative_exposure": float(sum(dose_path)),
        **response,
        "active_tumor_auc": int(sum(total_tumor[THERAPY_START:THERAPY_END])),
        "final_sensitive": int(ca.history["sensitive"][-1]),
        "final_resistant": int(ca.history["resistant"][-1]),
        "stability": _stability_payload(stability),
        "tumor_trajectory_sha256": sha256(_trajectory_bytes(total_tumor)).hexdigest(),
        "final_grid_sha256": sha256(_grid_bytes(ca.grid)).hexdigest(),
    }


def _closed_loop(seed: int, raw_division_rate: float, cutoff: int) -> dict:
    def dose_at_step(ca: AdvancedTumorCA, step: int) -> float:
        if not THERAPY_START <= step < THERAPY_END:
            return 0.0
        burden = int(
            np.count_nonzero(ca.grid == ca.TUMOR_SENSITIVE)
            + np.count_nonzero(ca.grid == ca.TUMOR_RESISTANT)
        )
        return HIGH_DOSE if burden > cutoff else LOW_DOSE

    return _run(seed, raw_division_rate, dose_at_step)


def _yoked(seed: int, raw_division_rate: float, doses: tuple[float, ...]) -> dict:
    _require(len(doses) == STEPS, "yoked dose path has the wrong length")
    return _run(seed, raw_division_rate, lambda _ca, step: doses[step])


def _key(seed: int, semantic: str, cutoff: str) -> str:
    return f"{seed}:{semantic}:{cutoff}"


def _cross_key(
    seed: int,
    target_semantic: str,
    source_semantic: str,
    cutoff: str,
) -> str:
    return f"{seed}:target={target_semantic}:path={source_semantic}:{cutoff}"


def _metric(row: dict, name: str) -> float | int:
    if name == "stability_score":
        return row["stability"]["stability_score"]
    return row[name]


def build_payload() -> dict:
    closed: dict[str, dict] = {}
    for seed in SEEDS:
        for semantic, raw_rate in SEMANTICS.items():
            for cutoff_name, cutoff in CUTOFFS.items():
                closed[_key(seed, semantic, cutoff_name)] = _closed_loop(
                    seed, raw_rate, cutoff
                )

    cross: dict[str, dict] = {}
    for seed in SEEDS:
        for cutoff_name in CUTOFFS:
            legacy = closed[_key(seed, "legacy", cutoff_name)]
            unit = closed[_key(seed, "unit_interval", cutoff_name)]
            cross[_cross_key(seed, "unit_interval", "legacy", cutoff_name)] = _yoked(
                seed, SEMANTICS["unit_interval"], tuple(legacy["dose_path"])
            )
            cross[_cross_key(seed, "legacy", "unit_interval", cutoff_name)] = _yoked(
                seed, SEMANTICS["legacy"], tuple(unit["dose_path"])
            )

    metric_names = (
        "response_pretherapy_pct",
        "response_inherited_post_first_dose_pct",
        "final_tumor_burden",
        "active_tumor_auc",
        "final_resistant",
        "stability_score",
    )
    decompositions: dict[str, dict] = {}
    for seed in SEEDS:
        for cutoff_name in CUTOFFS:
            legacy_legacy = closed[_key(seed, "legacy", cutoff_name)]
            unit_unit = closed[_key(seed, "unit_interval", cutoff_name)]
            unit_legacy = cross[
                _cross_key(seed, "unit_interval", "legacy", cutoff_name)
            ]
            legacy_unit = cross[
                _cross_key(seed, "legacy", "unit_interval", cutoff_name)
            ]
            rows = {}
            for metric_name in metric_names:
                ll = _metric(legacy_legacy, metric_name)
                uu = _metric(unit_unit, metric_name)
                ul = _metric(unit_legacy, metric_name)
                lu = _metric(legacy_unit, metric_name)
                total = uu - ll
                direct_legacy_path = ul - ll
                path_under_unit = uu - ul
                path_under_legacy = lu - ll
                direct_unit_path = uu - lu
                _require(
                    bool(
                        np.isclose(
                            total,
                            direct_legacy_path + path_under_unit,
                            rtol=0,
                            atol=1e-12,
                        )
                    ),
                    f"legacy-path decomposition failed for {seed}/{cutoff_name}/{metric_name}",
                )
                _require(
                    bool(
                        np.isclose(
                            total,
                            path_under_legacy + direct_unit_path,
                            rtol=0,
                            atol=1e-12,
                        )
                    ),
                    f"unit-path decomposition failed for {seed}/{cutoff_name}/{metric_name}",
                )
                rows[metric_name] = {
                    "total_semantics": total,
                    "semantics_on_legacy_path": direct_legacy_path,
                    "unit_path_substitution": path_under_unit,
                    "legacy_path_substitution": path_under_legacy,
                    "semantics_on_unit_path": direct_unit_path,
                }
            decompositions[f"{seed}:{cutoff_name}"] = rows

    observed_high_steps = {key: row["high_dose_steps"] for key, row in closed.items()}
    _require(
        observed_high_steps == EXPECTED_HIGH_DOSE_STEPS,
        "closed-loop high-dose exposure fixture drifted",
    )
    all_rows = {**closed, **cross}
    for key, row in all_rows.items():
        _validate_dose_window(key, row)

    exact_closed_loop_replays = 0
    for seed in SEEDS:
        for cutoff_name in CUTOFFS:
            for target_semantic, source_semantic in (
                ("unit_interval", "legacy"),
                ("legacy", "unit_interval"),
            ):
                cross_row = cross[
                    _cross_key(seed, target_semantic, source_semantic, cutoff_name)
                ]
                source_row = closed[_key(seed, source_semantic, cutoff_name)]
                target_row = closed[_key(seed, target_semantic, cutoff_name)]
                _require(
                    cross_row["dose_path"] == source_row["dose_path"],
                    "cross-yoked path diverged from its named source for "
                    f"{seed}/{target_semantic}/{source_semantic}/{cutoff_name}",
                )
                _require(
                    cross_row["dose_sha256"] == source_row["dose_sha256"],
                    "cross-yoked dose hash diverged from its named source for "
                    f"{seed}/{target_semantic}/{source_semantic}/{cutoff_name}",
                )
                if (
                    cross_row["dose_sha256"] == target_row["dose_sha256"]
                    and cross_row["tumor_trajectory_sha256"]
                    == target_row["tumor_trajectory_sha256"]
                    and cross_row["final_grid_sha256"]
                    == target_row["final_grid_sha256"]
                ):
                    exact_closed_loop_replays += 1

        legacy = closed[_key(seed, "legacy", "capacity_scaled")]
        unit = closed[_key(seed, "unit_interval", "capacity_scaled")]
        _require(
            legacy["dose_path"] == unit["dose_path"],
            f"scaled common-exposure path diverged for seed {seed}",
        )
        _require(
            legacy["high_dose_steps"] == 100 and legacy["low_dose_steps"] == 0,
            f"scaled controller was not all-high for seed {seed}",
        )

    execution_summary = {
        "closed_loop_executions": len(closed),
        "cross_yoked_executions": len(cross),
        "total_executions": len(all_rows),
        "unique_tumor_trajectories": len(
            {row["tumor_trajectory_sha256"] for row in all_rows.values()}
        ),
        "unique_dose_paths": len({row["dose_sha256"] for row in all_rows.values()}),
        "exact_closed_loop_replays": exact_closed_loop_replays,
    }
    _require(
        execution_summary
        == {
            "closed_loop_executions": 12,
            "cross_yoked_executions": 12,
            "total_executions": 24,
            "unique_tumor_trajectories": 16,
            "unique_dose_paths": 4,
            "exact_closed_loop_replays": 8,
        },
        "execution and replay-count fixture drifted",
    )

    fixture = {
        "closed_loop": closed,
        "cross_yoked": cross,
        "decompositions": decompositions,
        "execution_summary": execution_summary,
    }
    fixture_digest = _canonical_digest(fixture)
    _require(
        fixture_digest == EXPECTED_FIXTURE_SHA256,
        "adaptive factorial fixture drifted: "
        f"expected {EXPECTED_FIXTURE_SHA256}, observed {fixture_digest}",
    )

    return {
        "classification": "INCREMENTAL / EMPIRICAL bounded software-model audit",
        "scope": {
            "size": SIZE,
            "steps": STEPS,
            "seeds": SEEDS,
            "therapy_window_steps": {
                "start_inclusive": THERAPY_START,
                "end_exclusive": THERAPY_END,
            },
            "response_history_indices": {
                "pretherapy_baseline": PRETHERAPY_BASELINE_INDEX,
                "inherited_post_first_dose_baseline": POST_FIRST_DOSE_BASELINE_INDEX,
                "nadir_start_inclusive": THERAPY_START,
                "nadir_stop_exclusive": RESPONSE_NADIR_STOP_EXCLUSIVE,
            },
            "semantics": SEMANTICS,
            "cutoffs": CUTOFFS,
            "core_cutoff_fraction": 500 / (120 * 120),
            "scaled_cutoff_fraction": CUTOFFS["capacity_scaled"] / (SIZE * SIZE),
            "fixture_sha256": fixture_digest,
            "biological_or_clinical_claim": False,
        },
        **fixture,
    }


def main() -> None:
    print(json.dumps(build_payload(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
