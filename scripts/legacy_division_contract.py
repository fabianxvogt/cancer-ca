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
import copy
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, Optional


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


_CONTRACT_ASSIGNMENTS = {
    "local_division_rate": {
        "class_name": "AdvancedTumorCA",
        "method_name": "__init__",
        "receiver": "self",
    },
    "division_prob": {
        "class_name": "AdvancedTumorCA",
        "method_name": "rule_a_proliferation",
        "receiver": None,
    },
}


def _safe_path_text(path: Path) -> str:
    """Keep control characters in path errors from creating extra output lines."""

    text = str(path)
    return text if text.isprintable() else repr(text)[1:-1]


def _scoped_method(tree: ast.AST, class_name: str, method_name: str) -> ast.AST:
    """Return one top-level class method used by the source contract."""

    classes = [
        node
        for node in getattr(tree, "body", [])
        if isinstance(node, ast.ClassDef) and node.name == class_name
    ]
    if len(classes) != 1:
        raise ValueError(f"expected exactly one top-level class {class_name!r}")

    methods = [
        node
        for node in classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == method_name
    ]
    if len(methods) != 1:
        raise ValueError(
            f"expected exactly one method {class_name}.{method_name}"
        )
    return methods[0]


def _scoped_nodes(method: ast.AST):
    """Yield statement descendants without entering nested definitions."""

    pending = list(method.body)
    while pending:
        node = pending.pop()
        yield node
        if isinstance(
            node,
            (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            continue
        pending.extend(ast.iter_child_nodes(node))


def _import_binding_name(alias: ast.alias) -> str:
    """Return the name bound by one import alias in a local scope."""

    if alias.asname:
        return alias.asname
    return alias.name.split(".", 1)[0]


def _binding_targets(node: ast.AST):
    """Return method-scope binding targets that could shadow a contract value."""

    if isinstance(node, ast.Assign):
        return node.targets
    if isinstance(node, (ast.AnnAssign, ast.AugAssign)):
        return [node.target]
    if isinstance(node, (ast.For, ast.AsyncFor)):
        return [node.target]
    if isinstance(node, ast.NamedExpr):
        return [node.target]
    if isinstance(node, (ast.With, ast.AsyncWith)):
        return [
            item.optional_vars
            for item in node.items
            if item.optional_vars is not None
        ]
    if isinstance(node, ast.ExceptHandler) and node.name:
        return [ast.Name(id=node.name, ctx=ast.Store())]
    if isinstance(node, ast.Import):
        return [
            ast.Name(id=_import_binding_name(alias), ctx=ast.Store())
            for alias in node.names
        ]
    if isinstance(node, ast.ImportFrom):
        return [
            ast.Name(id=_import_binding_name(alias), ctx=ast.Store())
            for alias in node.names
            if alias.name != "*"
        ]
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [ast.Name(id=node.name, ctx=ast.Store())]
    return []


def _mentions_target(target: ast.AST, target_name: str) -> bool:
    """Check binding positions without treating target expressions as bindings."""

    if isinstance(target, ast.Name):
        return target.id == target_name
    if isinstance(target, ast.Attribute):
        return target.attr == target_name
    if isinstance(target, (ast.List, ast.Tuple)):
        return any(
            _mentions_target(element, target_name)
            for element in target.elts
        )
    if isinstance(target, ast.Starred):
        return _mentions_target(target.value, target_name)
    return False


def _is_expected_target(
    target: ast.AST, target_name: str, receiver: Optional[str]
) -> bool:
    if receiver is None:
        return isinstance(target, ast.Name) and target.id == target_name
    return (
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == receiver
        and target.attr == target_name
    )


def _assignment(tree: ast.AST, target_name: str) -> ast.AST:
    """Return one exact contract assignment from its declared source scope."""

    try:
        spec = _CONTRACT_ASSIGNMENTS[target_name]
    except KeyError as exc:
        raise ValueError(f"unknown contract assignment {target_name!r}") from exc

    method = _scoped_method(tree, spec["class_name"], spec["method_name"])
    candidates = []
    for node in _scoped_nodes(method):
        targets = _binding_targets(node)
        if any(_mentions_target(target, target_name) for target in targets):
            candidates.append(node)

    if len(candidates) > 1:
        raise ValueError(f"multiple assignments found for {target_name!r}")
    if not candidates:
        raise ValueError(
            f"could not find assignment for {target_name!r} in "
            f"{spec['class_name']}.{spec['method_name']}"
        )

    node = candidates[0]
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        raise ValueError(
            f"{target_name} must use one plain assignment in "
            f"{spec['class_name']}.{spec['method_name']}"
        )
    if not _is_expected_target(node.targets[0], target_name, spec["receiver"]):
        expected = (
            f"{spec['receiver']}.{target_name}"
            if spec["receiver"]
            else target_name
        )
        raise ValueError(
            f"{target_name} must target {expected} in "
            f"{spec['class_name']}.{spec['method_name']}"
        )
    return node.value


def _right_hand_constant(expression: ast.AST, label: str) -> float:
    """Extract the scalar multiplier from an explicit multiplication."""

    if not isinstance(expression, ast.BinOp) or not isinstance(expression.op, ast.Mult):
        raise ValueError(f"{label} must remain an explicit multiplication")
    value = expression.right
    if not isinstance(value, ast.Constant) or type(value.value) not in (int, float):
        raise ValueError(f"{label} must use a numeric scalar multiplier")
    try:
        result = float(value.value)
    except OverflowError as exc:
        raise ValueError(f"{label} multiplier must be finite") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} multiplier must be finite")
    if label == "division_prob" and result <= 0.0:
        raise ValueError(
            "division_prob multiplier must be positive to report saturation"
        )
    return result


def _finite_derived(value: float, label: str) -> float:
    """Reject finite source constants whose derived report value overflows."""

    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def _calibration_rows(gate_scale: float) -> list[Dict[str, Any]]:
    """Return the memo's raw-rate threshold table without drawing randomness."""

    rows = []
    for raw_rate in CALIBRATION_RAW_RATES:
        threshold = _finite_derived(
            raw_rate * gate_scale, "calibration gate threshold"
        )
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

    boundary = _finite_derived(
        1.0 / gate_scale, "saturation raw-rate boundary"
    )
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

    path_text = _safe_path_text(path)
    if not path.is_file():
        raise ValueError(f"source path must be a regular file: {path_text}")
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeError as exc:
        raise ValueError(
            f"could not decode source path {path_text} as UTF-8: {exc}"
        ) from exc
    except OSError as exc:
        raise ValueError(f"could not read source path {path_text}: {exc}") from exc
    tree = ast.parse(source, filename=path_text)
    rate_expression = _assignment(tree, "local_division_rate")
    gate_expression = _assignment(tree, "division_prob")
    default_rate = _right_hand_constant(rate_expression, "local_division_rate")
    gate_scale = _right_hand_constant(gate_expression, "division_prob")
    threshold = _finite_derived(
        default_rate * gate_scale, "default division threshold"
    )

    return {
        "source": str(path),
        "default_rate": default_rate,
        "gate_scale": gate_scale,
        "default_threshold": threshold,
        "threshold_in_unit_interval": 0.0 <= threshold <= 1.0,
        "calibration_thresholds": _calibration_rows(gate_scale),
        "saturation": _saturation_contract(gate_scale),
        # Return an isolated payload so callers cannot mutate future reports.
        "owner_decision_boundary": copy.deepcopy(OWNER_DECISION_BOUNDARY),
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
    try:
        report = inspect_contract(args.path)
    except (SyntaxError, ValueError) as exc:
        print(f"CONTRACT BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
