#!/usr/bin/env python3
"""Bounded fixed-seed sensitivity audit for division-rate semantics."""

from __future__ import annotations

from hashlib import sha256
import json

import numpy as np

from stability_metrics import ResponseVsStability, StabilityMetrics
from tumor_ca import AdvancedTumorCA


SIZE = 24
STEPS = 180
SEED = 42
THERAPY_START = 25
LEGACY_RAW_DIVISION_RATE = 4.0
SEMANTICS = {"legacy": 4.0, "bernoulli_screen": 1.0}
STRATEGIES = {
    "MTD": {"intensity": 0.50, "duration": 40, "type": "continuous"},
    "Moderate Continuous": {
        "intensity": 0.35,
        "duration": 75,
        "type": "continuous",
    },
    "Intermittent High": {
        "intensity": 0.45,
        "duration": 20,
        "type": "intermittent",
        "cycles": 3,
        "gap": 25,
    },
    "Adaptive Low": {"intensity": 0.25, "duration": 100, "type": "adaptive"},
    "Metronomic": {"intensity": 0.15, "duration": 125, "type": "continuous"},
}

# This digest pins every emitted metric, state count, normalized grid hash,
# trajectory hash, and dose-exposure count in the two fixed-seed result tables.
# It is intentionally updated only when the bounded fixture is rebaselined.
EXPECTED_RESULTS_SHA256 = (
    "bdf2a054cc0a2ab8b938348c28305c00a570f85b0cb4830a86abb29a39fd228d"
)
EXPECTED_DIFFERENT_CELLS = {
    "MTD": 326,
    "Moderate Continuous": 282,
    "Intermittent High": 304,
    "Adaptive Low": 293,
    "Metronomic": 256,
}
EXPECTED_RANKINGS = {
    "response": {
        "legacy": [
            "Metronomic",
            "Moderate Continuous",
            "Adaptive Low",
            "Intermittent High",
            "MTD",
        ],
        "bernoulli_screen": [
            "Metronomic",
            "Moderate Continuous",
            "Adaptive Low",
            "Intermittent High",
            "MTD",
        ],
    },
    "final_burden": {
        "legacy": [
            "Metronomic",
            "Moderate Continuous",
            "Adaptive Low",
            "Intermittent High",
            "MTD",
        ],
        "bernoulli_screen": [
            "Metronomic",
            "Moderate Continuous",
            "Adaptive Low",
            "Intermittent High",
            "MTD",
        ],
    },
    "stability": {
        "legacy": [
            "MTD",
            "Adaptive Low",
            "Intermittent High",
            "Moderate Continuous",
            "Metronomic",
        ],
        "bernoulli_screen": [
            "MTD",
            "Intermittent High",
            "Adaptive Low",
            "Moderate Continuous",
            "Metronomic",
        ],
    },
}


def _require(condition: bool, message: str) -> None:
    """Raise a validation failure that remains active under ``python -O``."""
    if not condition:
        raise RuntimeError(message)


def _grid_bytes(grid: np.ndarray) -> bytes:
    """Return a platform-independent byte representation for state grids."""
    return np.asarray(grid, dtype=np.uint8).tobytes(order="C")


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def _set_therapy(ca: AdvancedTumorCA, intensity: float) -> None:
    ca.therapy = np.ones((SIZE, SIZE)) * intensity


def run_strategy(name: str, raw_division_rate: float) -> tuple[dict, np.ndarray, str]:
    """Run one declared strategy under one constructor-rate counterfactual."""
    config = STRATEGIES[name]
    ca = AdvancedTumorCA(size=SIZE, seed=SEED)
    ca.initialize_tumor(radius=5, normal_cells=False)
    _require(
        bool(np.all(ca.local_division_rate == LEGACY_RAW_DIVISION_RATE)),
        "AdvancedTumorCA constructor no longer initializes the legacy 4.0 rate",
    )
    ca.local_division_rate.fill(raw_division_rate)

    therapy_active = False
    cycle_count = 0
    last_therapy_end = THERAPY_START
    therapy_step_counts: dict[str, int] = {}
    trajectory_hasher = sha256()

    for step in range(STEPS):
        if config["type"] == "continuous":
            if step == THERAPY_START:
                _set_therapy(ca, config["intensity"])
                therapy_active = True
            if step == THERAPY_START + config["duration"]:
                _set_therapy(ca, 0.0)
                therapy_active = False
        elif config["type"] == "intermittent":
            cycle_start = THERAPY_START + cycle_count * (
                config["duration"] + config["gap"]
            )
            if step == cycle_start and cycle_count < config["cycles"]:
                _set_therapy(ca, config["intensity"])
                therapy_active = True
            if therapy_active and step >= cycle_start + config["duration"]:
                _set_therapy(ca, 0.0)
                therapy_active = False
                cycle_count += 1
                last_therapy_end = step
        elif config["type"] == "adaptive":
            if THERAPY_START <= step < THERAPY_START + config["duration"]:
                tumor = int(
                    np.count_nonzero(ca.grid == ca.TUMOR_SENSITIVE)
                    + np.count_nonzero(ca.grid == ca.TUMOR_RESISTANT)
                )
                intensity = (
                    config["intensity"] if tumor > 500 else config["intensity"] * 0.5
                )
                _set_therapy(ca, intensity)
            elif step >= THERAPY_START + config["duration"]:
                _set_therapy(ca, 0.0)
        else:  # pragma: no cover - fixed local configuration
            raise ValueError(f"unknown strategy type: {config['type']}")

        dose = f"{float(np.max(ca.therapy)):.3f}"
        therapy_step_counts[dose] = therapy_step_counts.get(dose, 0) + 1
        ca.step()
        trajectory_hasher.update(step.to_bytes(4, byteorder="big", signed=False))
        trajectory_hasher.update(_grid_bytes(ca.grid))

    therapy_end = THERAPY_START + config["duration"]
    if config["type"] == "intermittent":
        therapy_end = last_therapy_end
    response = ResponseVsStability.measure_response(
        ca.history, THERAPY_START, therapy_end
    )
    stability = StabilityMetrics.compute_all_metrics(
        ca.history, THERAPY_START, therapy_end
    )
    grid = ca.grid.copy()
    row = {
        "response_pct": float(response["max_reduction"]),
        "final_tumor_burden": int(response["final_tumor_burden"]),
        "stability_score": float(stability["stability_score"]),
        "control_horizon": int(stability["control_horizon"]),
        "state_counts": [int(np.count_nonzero(grid == state)) for state in range(5)],
        "grid_sha256": sha256(_grid_bytes(grid)).hexdigest(),
        "trajectory_sha256": trajectory_hasher.hexdigest(),
        "therapy_step_counts": therapy_step_counts,
    }
    return row, grid, trajectory_hasher.hexdigest()


def _ordered(rows: dict[str, dict], metric: str, reverse: bool) -> list[str]:
    return sorted(rows, key=lambda name: rows[name][metric], reverse=reverse)


def _spearman(left: list[str], right: list[str]) -> float:
    positions = {name: index for index, name in enumerate(right)}
    squared = sum((index - positions[name]) ** 2 for index, name in enumerate(left))
    count = len(left)
    return 1.0 - 6.0 * squared / (count * (count * count - 1))


def _kendall(left: list[str], right: list[str]) -> float:
    positions = {name: index for index, name in enumerate(right)}
    concordant = 0
    discordant = 0
    for first in range(len(left)):
        for second in range(first + 1, len(left)):
            if positions[left[first]] < positions[left[second]]:
                concordant += 1
            else:
                discordant += 1
    return (concordant - discordant) / (concordant + discordant)


def build_payload() -> dict:
    """Run and validate the declared fixed-seed fixture."""
    results: dict[str, dict[str, dict]] = {}
    grids: dict[str, dict[str, np.ndarray]] = {}
    trajectories: dict[str, dict[str, str]] = {}
    for semantic, raw_rate in SEMANTICS.items():
        results[semantic] = {}
        grids[semantic] = {}
        trajectories[semantic] = {}
        for name in STRATEGIES:
            row, grid, trajectory_hash = run_strategy(name, raw_rate)
            results[semantic][name] = row
            grids[semantic][name] = grid
            trajectories[semantic][name] = trajectory_hash

    replay = {}
    for semantic, raw_rate in SEMANTICS.items():
        row, grid, trajectory_hash = run_strategy("MTD", raw_rate)
        replay[semantic] = {
            "summary_equal": row == results[semantic]["MTD"],
            "final_grid_equal": bool(np.array_equal(grid, grids[semantic]["MTD"])),
            "trajectory_equal": (trajectory_hash == trajectories[semantic]["MTD"]),
        }
        _require(
            replay[semantic]
            == {
                "summary_equal": True,
                "final_grid_equal": True,
                "trajectory_equal": True,
            },
            f"{semantic} MTD replay diverged",
        )

    comparisons = {}
    for name in STRATEGIES:
        legacy = results["legacy"][name]
        alternative = results["bernoulli_screen"][name]
        different = int(
            np.count_nonzero(grids["legacy"][name] != grids["bernoulli_screen"][name])
        )
        comparisons[name] = {
            "response_delta_pp": alternative["response_pct"] - legacy["response_pct"],
            "final_burden_delta": alternative["final_tumor_burden"]
            - legacy["final_tumor_burden"],
            "stability_delta": alternative["stability_score"]
            - legacy["stability_score"],
            "different_cells": different,
            "different_fraction": different / (SIZE * SIZE),
        }

    ranking_specs = {
        "response": ("response_pct", True),
        "final_burden": ("final_tumor_burden", False),
        "stability": ("stability_score", True),
    }
    rankings = {}
    for label, (metric, reverse) in ranking_specs.items():
        legacy_order = _ordered(results["legacy"], metric, reverse)
        alternative_order = _ordered(results["bernoulli_screen"], metric, reverse)
        rankings[label] = {
            "legacy": legacy_order,
            "bernoulli_screen": alternative_order,
            "spearman": _spearman(legacy_order, alternative_order),
            "kendall": _kendall(legacy_order, alternative_order),
            "exact_order_match": legacy_order == alternative_order,
        }

    observed_orders = {
        label: {
            semantic: rankings[label][semantic]
            for semantic in ("legacy", "bernoulli_screen")
        }
        for label in ranking_specs
    }
    _require(observed_orders == EXPECTED_RANKINGS, "named strategy rankings drifted")
    _require(
        {name: row["different_cells"] for name, row in comparisons.items()}
        == EXPECTED_DIFFERENT_CELLS,
        "final-grid difference counts drifted",
    )
    _require(
        all(
            row["control_horizon"] == 1
            for semantic_rows in results.values()
            for row in semantic_rows.values()
        ),
        "the all-ones control-horizon fixture drifted",
    )
    results_digest = _canonical_digest(results)
    _require(
        results_digest == EXPECTED_RESULTS_SHA256,
        "fixed-seed result fixture drifted: "
        f"expected {EXPECTED_RESULTS_SHA256}, observed {results_digest}",
    )

    return {
        "classification": "INCREMENTAL / EMPIRICAL bounded sensitivity audit",
        "scope": {
            "size": SIZE,
            "steps": STEPS,
            "seed": SEED,
            "therapy_start": THERAPY_START,
            "raw_division_rates": SEMANTICS,
            "adaptive_cutoff_cells": 500,
            "adaptive_cutoff_fraction": 500 / (SIZE * SIZE),
            "result_fixture_sha256": results_digest,
            "biological_or_clinical_claim": False,
        },
        "results": results,
        "comparisons": comparisons,
        "rankings": rankings,
        "replay": replay,
    }


def main() -> None:
    payload = build_payload()
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
