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
