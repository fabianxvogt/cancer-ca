#!/usr/bin/env python3
"""Run a bounded, dependency-aware structural smoke of the core experiment.

This command checks that the five strategy branches import and return complete
histories. It intentionally does not calculate response/stability metrics or
support scientific interpretation of the bounded run.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Iterable, Mapping


DEFAULT_SIZE = 32
DEFAULT_STEPS = 205
DEFAULT_SEED = 42
THERAPY_START = 200

EXPECTED_STRATEGIES = (
    "MTD - Maximum Tolerated Dose",
    "Moderate Continuous",
    "Intermittent High",
    "Adaptive Low",
    "Metronomic",
)
EXPECTED_HISTORY_KEYS = frozenset(
    {
        "sensitive",
        "resistant",
        "dead",
        "normal",
        "entropy",
        "edge_complexity",
        "total_tumor",
    }
)
REQUIRED_IMPORTS = {
    "numpy": "numpy",
    "scipy": "scipy",
    "matplotlib": "matplotlib",
    "sklearn": "scikit-learn",
    "pandas": "pandas",
}


def missing_dependencies() -> tuple[str, ...]:
    """Return pinned research dependencies unavailable to this interpreter."""

    return tuple(
        distribution
        for module, distribution in REQUIRED_IMPORTS.items()
        if importlib.util.find_spec(module) is None
    )


def validate_results(results: Iterable[Mapping[str, Any]], steps: int) -> dict[str, Any]:
    """Validate the structural contract exercised by the bounded smoke."""

    rows = list(results)
    if len(rows) != len(EXPECTED_STRATEGIES):
        raise AssertionError(
            f"expected {len(EXPECTED_STRATEGIES)} strategies, got {len(rows)}"
        )

    names = tuple(row.get("name") for row in rows)
    if names != EXPECTED_STRATEGIES:
        raise AssertionError(f"unexpected strategy order: {names!r}")

    history_lengths: set[int] = set()
    for row in rows:
        history = row.get("history")
        if not isinstance(history, Mapping):
            raise AssertionError(f"{row['name']!r} has no history mapping")
        if set(history) != EXPECTED_HISTORY_KEYS:
            raise AssertionError(
                f"{row['name']!r} has unexpected history keys: {set(history)!r}"
            )
        lengths = {len(values) for values in history.values()}
        if lengths != {steps}:
            raise AssertionError(
                f"{row['name']!r} history lengths are {sorted(lengths)!r}, "
                f"expected {steps}"
            )
        if row.get("therapy_start") != THERAPY_START:
            raise AssertionError(
                f"{row['name']!r} starts therapy at {row.get('therapy_start')!r}, "
                f"expected {THERAPY_START}"
            )
        history_lengths.update(lengths)

    return {
        "strategies": len(rows),
        "strategy_names": list(names),
        "history_lengths": sorted(history_lengths),
        "therapy_start": THERAPY_START,
        "scope": "structural import/branch/shape check; no scientific result claim",
    }


def run_smoke(
    size: int = DEFAULT_SIZE,
    steps: int = DEFAULT_STEPS,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Run the bounded core experiment and return a structural summary."""

    if size < 1:
        raise ValueError("size must be positive")
    if steps < THERAPY_START + 1:
        raise ValueError(f"steps must be at least {THERAPY_START + 1}")

    missing = missing_dependencies()
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(
            f"missing research dependencies: {names}. "
            "Install the pinned environment with: "
            "python3 -m pip install -r requirements.txt"
        )

    # Import only after the dependency check so an incomplete environment gets
    # an actionable message rather than a traceback from a transitive import.
    from core_experiment import run_controlled_experiment

    # The core runner prints progress but does not return it; keep this entry
    # point's output to the concise smoke summary below.
    with redirect_stdout(StringIO()):
        results = run_controlled_experiment(size=size, steps=steps, seed=seed)

    summary = validate_results(results, steps=steps)
    summary.update({"size": size, "steps": steps, "seed": seed})
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a bounded structural smoke of core_experiment. "
            "This is not a scientific validation run."
        )
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the structural summary as JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = run_smoke()
    except (RuntimeError, ValueError, AssertionError) as exc:
        print(f"SMOKE BLOCKED: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(summary, sort_keys=True))
    else:
        print("SMOKE PASS")
        print(f"parameters: size={summary['size']}, steps={summary['steps']}, seed={summary['seed']}")
        print(f"strategies: {summary['strategies']}")
        print(f"history_lengths: {summary['history_lengths']}")
        print(f"scope: {summary['scope']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
