#!/usr/bin/env python3
"""Run a bounded, dependency-aware structural smoke of the core experiment.

This command checks that the five strategy branches import and return complete
histories. It intentionally does not calculate response/stability metrics or
support scientific interpretation of the bounded run.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
from importlib import metadata
from pathlib import Path
import re
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
REQUIREMENTS_PATH = Path(__file__).resolve().parents[1] / "requirements.txt"
CORE_EXPERIMENT_PATH = Path(__file__).resolve().parents[1] / "core_experiment.py"
DUAL_METRIC_FIGURE_PATH = Path(__file__).resolve().parents[1] / "figure_S1_metric_dependence.py"
PROJECT_MODULES = frozenset({"tumor_ca", "stability_metrics"})
SOURCE_PIN_CONTRACTS = {
    "core_experiment.py": CORE_EXPERIMENT_PATH,
    "figure_S1_metric_dependence.py": DUAL_METRIC_FIGURE_PATH,
}


def _normalize_distribution_name(name: str) -> str:
    """Normalize a distribution name using the packaging name convention."""

    return re.sub(r"[-_.]+", "-", name.strip()).lower()


def pinned_requirements(path: Path = REQUIREMENTS_PATH) -> dict[str, str]:
    """Read exact ``name==version`` pins from the research requirements file."""

    requirements: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if "==" not in line:
            raise ValueError(
                f"{path}:{line_number}: expected an exact name==version pin"
            )
        raw_name, raw_version = line.split("==", 1)
        name = _normalize_distribution_name(raw_name)
        version = raw_version.strip()
        if not name or not version or re.search(r"\s", version):
            raise ValueError(
                f"{path}:{line_number}: invalid exact name==version pin"
            )
        previous = requirements.get(name)
        if previous is not None and previous != version:
            raise ValueError(f"{path}:{line_number}: conflicting pin for {name}")
        requirements[name] = version
    if not requirements:
        raise ValueError(f"{path}: no exact dependency pins found")
    return requirements


def required_dependency_pin_gaps(
    requirements: Mapping[str, str] | None = None,
) -> tuple[str, ...]:
    """Return required distributions that have no exact requirements pin.

    This is a metadata-only check. It does not import a dependency, execute the
    model, or establish that any scientific result is reproducible.
    """

    pins = (
        pinned_requirements()
        if requirements is None
        else {
            _normalize_distribution_name(name): version
            for name, version in requirements.items()
        }
    )
    required_distributions = {
        _normalize_distribution_name(distribution)
        for distribution in REQUIRED_IMPORTS.values()
    }
    return tuple(sorted(required_distributions - pins.keys()))


def direct_imported_modules(path: Path = CORE_EXPERIMENT_PATH) -> tuple[str, ...]:
    """Return direct top-level imports from a project source file.

    This is a source-only inspection. It excludes the two project modules that
    the runner imports locally and does not import any discovered module.
    """

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module.split(".", 1)[0])
    return tuple(sorted(modules - PROJECT_MODULES))


def source_dependency_pin_gaps(
    path: Path = CORE_EXPERIMENT_PATH,
    requirements: Mapping[str, str] | None = None,
    import_to_distribution: Mapping[str, str] | None = None,
) -> tuple[str, ...]:
    """Return static direct-import gaps in a source file's exact pin coverage.

    The result is metadata only: it parses source and requirements text, does
    not import dependencies, execute the model, or establish comparability.
    """

    pins = (
        pinned_requirements()
        if requirements is None
        else {
            _normalize_distribution_name(name): version
            for name, version in requirements.items()
        }
    )
    import_map = REQUIRED_IMPORTS if import_to_distribution is None else import_to_distribution
    gaps: list[str] = []
    for module in direct_imported_modules(path):
        distribution = import_map.get(module)
        if distribution is None:
            gaps.append(f"{module} has no distribution mapping")
            continue
        normalized_distribution = _normalize_distribution_name(distribution)
        if normalized_distribution not in pins:
            gaps.append(f"{module} -> {distribution}")
    return tuple(gaps)


def dependency_version_mismatches(
    requirements: Mapping[str, str] | None = None,
    version_lookup: Any = None,
) -> tuple[str, ...]:
    """Return human-readable mismatches between pins and installed distributions."""

    expected = dict(pinned_requirements() if requirements is None else requirements)
    lookup = metadata.version if version_lookup is None else version_lookup
    mismatches: list[str] = []
    for name, expected_version in sorted(expected.items()):
        try:
            actual_version = lookup(name)
        except metadata.PackageNotFoundError:
            mismatches.append(f"{name} missing (expected {expected_version})")
            continue
        if actual_version != expected_version:
            mismatches.append(
                f"{name}=={actual_version} installed (expected {expected_version})"
            )
    return tuple(mismatches)


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

    for source_label, source_path in SOURCE_PIN_CONTRACTS.items():
        source_pin_gaps = source_dependency_pin_gaps(source_path)
        if source_pin_gaps:
            details = ", ".join(source_pin_gaps)
            raise RuntimeError(
                f"{source_label} direct imports lack exact distribution pins: "
                f"{details}"
            )

    pin_gaps = required_dependency_pin_gaps()
    if pin_gaps:
        names = ", ".join(pin_gaps)
        raise RuntimeError(
            "requirements.txt is missing exact pins for required smoke imports: "
            f"{names}"
        )

    missing = missing_dependencies()
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(
            f"missing research dependencies: {names}. "
            "Install the pinned environment with: "
            "python3 -m pip install -r requirements.txt"
        )

    mismatches = dependency_version_mismatches()
    if mismatches:
        details = "; ".join(mismatches)
        raise RuntimeError(
            "research dependency versions do not match requirements.txt: "
            f"{details}. Recreate the pinned environment with: "
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
    summary.update(
        {
            "size": size,
            "steps": steps,
            "seed": seed,
            "dependencies": pinned_requirements(),
        }
    )
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
