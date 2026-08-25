#!/usr/bin/env python3
"""Inspect the legacy division-gate semantics without importing the model.

The calibration question is intentionally kept separate from model execution.
This source-level probe reports the raw default multiplier, the gate scale, and
their derived threshold so a future rescaling can be compared explicitly.
It does not run a cellular automaton or make a scientific claim.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
from pathlib import Path
from typing import Any, Dict


SOURCE_PATH = Path(__file__).resolve().parents[1] / "tumor_ca.py"
CALIBRATION_RAW_RATES = (0.5, 1.0, 1.25, 4.0)

OWNER_DECISION_BOUNDARY = {
    "semantic_choice": (
        "Choose one operational meaning before changing `tumor_ca.py` or "
        "interpreting new results."
    ),
    "semantic_options": [
        "Bernoulli probability",
        "Rate/propensity",
        "Legacy eligibility score",
    ],
    "selected_semantics": None,
    "compatibility_choice": (
        "The human decision is therefore both a semantic choice and a "
        "compatibility choice: preserve the legacy behavior, or recalibrate "
        "it and accept that the seeded trajectories and published outputs may "
        "change."
    ),
    "experiment_authorization": (
        "No run is authorized by this memo alone. Before execution, the owner "
        "must name one matrix row, state whether the existing seed-7 fingerprint "
        "and committed outputs are a preservation requirement, and approve an "
        "isolated comparison harness. The harness must not edit `tumor_ca.py`, "
        "regenerate figures, update JSON results, or change dependencies."
    ),
}


def _assignment(tree: ast.AST, target_name: str) -> ast.AST:
    """Return the value assigned to a simple name or attribute."""

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == target_name:
            return node.value
        if isinstance(target, ast.Attribute) and target.attr == target_name:
            return node.value
    raise ValueError(f"could not find assignment for {target_name!r}")


def _right_hand_constant(expression: ast.AST, label: str) -> float:
    """Extract the scalar multiplier from an explicit multiplication."""

    if not isinstance(expression, ast.BinOp) or not isinstance(expression.op, ast.Mult):
        raise ValueError(f"{label} must remain an explicit multiplication")
    value = expression.right
    if not isinstance(value, ast.Constant) or not isinstance(value.value, (int, float)):
        raise ValueError(f"{label} must use a numeric scalar multiplier")
    result = float(value.value)
    if not math.isfinite(result):
        raise ValueError(f"{label} multiplier must be finite")
    return result


def _calibration_rows(gate_scale: float) -> list[Dict[str, Any]]:
    """Return the memo's raw-rate threshold table without drawing randomness."""

    rows = []
    for raw_rate in CALIBRATION_RAW_RATES:
        threshold = raw_rate * gate_scale
        rows.append(
            {
                "raw_rate": raw_rate,
                "gate_threshold": threshold,
                "threshold_in_unit_interval": 0.0 <= threshold <= 1.0,
                "saturates_uniform_gate": threshold >= 1.0,
            }
        )
    return rows


def _saturation_contract(gate_scale: float) -> Dict[str, Any]:
    """Describe saturation implied by ``draw < gate_threshold`` for draws in [0, 1)."""

    boundary = 1.0 / gate_scale
    return {
        "draw_interval": "[0, 1)",
        "comparison": "draw < gate_threshold",
        "threshold_boundary": 1.0,
        "raw_rate_boundary": boundary,
        "saturates_when": "gate_threshold >= 1.0",
        "saturating_raw_rates": [
            row["raw_rate"]
            for row in _calibration_rows(gate_scale)
            if row["saturates_uniform_gate"]
        ],
        "behavior": (
            "Every eligible cell passes this gate at or above the raw-rate "
            f"boundary {boundary:g}; rates above that boundary are "
            "indistinguishable to this gate."
        ),
    }


def inspect_contract(path: Path = SOURCE_PATH) -> Dict[str, Any]:
    """Return the current source-level legacy division contract."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rate_expression = _assignment(tree, "local_division_rate")
    gate_expression = _assignment(tree, "division_prob")
    default_rate = _right_hand_constant(rate_expression, "local_division_rate")
    gate_scale = _right_hand_constant(gate_expression, "division_prob")
    threshold = default_rate * gate_scale

    return {
        "source": str(path),
        "default_rate": default_rate,
        "gate_scale": gate_scale,
        "default_threshold": threshold,
        "threshold_in_unit_interval": 0.0 <= threshold <= 1.0,
        "calibration_thresholds": _calibration_rows(gate_scale),
        "saturation": _saturation_contract(gate_scale),
        "owner_decision_boundary": OWNER_DECISION_BOUNDARY,
        "scope": "source-level legacy semantics contract; no model execution",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report legacy division-gate semantics without running the model."
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=SOURCE_PATH,
        help="path to tumor_ca.py (defaults to this project's model source)",
    )
    return parser


def main(argv: Any = None) -> int:
    args = build_parser().parse_args(argv)
    print(json.dumps(inspect_contract(args.path), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
