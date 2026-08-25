"""Focused tests for the dependency-aware structural smoke contract."""

import pytest
from importlib import metadata
from pathlib import Path

from scripts.smoke_core_experiment import (
    DUAL_METRIC_FIGURE_PATH,
    EXPECTED_HISTORY_KEYS,
    EXPECTED_STRATEGIES,
    FIGURE_SOURCE_INVENTORY,
    FIGURE_SOURCE_PIN_CONTRACTS,
    REQUIRED_IMPORTS,
    THERAPY_START,
    dependency_version_mismatches,
    direct_imported_modules,
    figure_source_inventory_gaps,
    pinned_requirements,
    required_dependency_pin_gaps,
    source_dependency_pin_gaps,
    manuscript_reference_gaps,
    validate_results,
)


def make_result(name, steps=205, therapy_start=THERAPY_START):
    return {
        "name": name,
        "therapy_start": therapy_start,
        "history": {key: [0] * steps for key in EXPECTED_HISTORY_KEYS},
    }


def test_validate_results_accepts_bounded_core_shape():
    summary = validate_results(
        [make_result(name) for name in EXPECTED_STRATEGIES],
        steps=205,
    )

    assert summary["strategies"] == 5
    assert summary["history_lengths"] == [205]
    assert summary["therapy_start"] == THERAPY_START
    assert "no scientific result claim" in summary["scope"]


def test_validate_results_rejects_incomplete_history():
    rows = [make_result(name) for name in EXPECTED_STRATEGIES]
    rows[0]["history"].pop("entropy")

    with pytest.raises(AssertionError, match="unexpected history keys"):
        validate_results(rows, steps=205)


def test_validate_results_rejects_short_smoke():
    rows = [make_result(name) for name in EXPECTED_STRATEGIES]
    rows[-1]["history"]["total_tumor"] = [0] * 204

    with pytest.raises(AssertionError, match="history lengths"):
        validate_results(rows, steps=205)


def test_pinned_requirements_reads_exact_pins_and_ignores_comments(tmp_path: Path):
    requirements = tmp_path / "requirements.txt"
    requirements.write_text(
        "# bounded research environment\n"
        "Demo_Package==1.2.3  # exact pin\n"
        "scikit_learn==4.5.6\n",
        encoding="utf-8",
    )

    assert pinned_requirements(requirements) == {
        "demo-package": "1.2.3",
        "scikit-learn": "4.5.6",
    }


def test_dependency_version_mismatches_reports_missing_and_drift():
    def lookup(name):
        if name == "missing-package":
            raise metadata.PackageNotFoundError(name)
        return "9.9.9"

    mismatches = dependency_version_mismatches(
        {"missing-package": "1.0.0", "drifted-package": "2.0.0"},
        version_lookup=lookup,
    )

    assert mismatches == (
        "drifted-package==9.9.9 installed (expected 2.0.0)",
        "missing-package missing (expected 1.0.0)",
    )


def test_pinned_requirements_rejects_unpinned_lines(tmp_path: Path):
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("numpy>=2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="exact name==version pin"):
        pinned_requirements(requirements)


def test_required_dependency_pin_gaps_accepts_current_requirements():
    assert required_dependency_pin_gaps() == ()


def test_required_dependency_pin_gaps_reports_missing_distribution_pins():
    gaps = required_dependency_pin_gaps(
        {
            "numpy": "2.0.2",
            "scikit_learn": "1.6.1",
        }
    )

    assert gaps == ("matplotlib", "pandas", "scipy", "seaborn")


def test_direct_import_contract_excludes_project_modules_and_finds_runner_deps():
    assert direct_imported_modules() == ("matplotlib", "numpy", "pandas")
    assert source_dependency_pin_gaps() == ()


def test_dual_metric_figure_import_contract_is_pinned():
    assert direct_imported_modules(DUAL_METRIC_FIGURE_PATH) == (
        "matplotlib",
        "numpy",
        "scipy",
    )
    assert source_dependency_pin_gaps(DUAL_METRIC_FIGURE_PATH) == ()


def test_all_committed_figure_scripts_have_pinned_direct_imports():
    assert REQUIRED_IMPORTS["seaborn"] == "seaborn"
    assert all(
        source_dependency_pin_gaps(path) == ()
        for path in FIGURE_SOURCE_PIN_CONTRACTS.values()
    )


def test_figure_source_inventory_matches_discovered_contract():
    assert figure_source_inventory_gaps() == ()
    assert all(
        (DUAL_METRIC_FIGURE_PATH.parent / name).is_file()
        for name in FIGURE_SOURCE_INVENTORY
    )


def test_figure_source_inventory_reports_added_and_removed_sources():
    assert figure_source_inventory_gaps(
        discovered={"figure1_concept.py", "figure8_new.py"},
        inventory={"figure1_concept.py", "figure2_main_result.py"},
    ) == (
        "figure8_new.py is not in the explicit figure-source inventory",
        "figure2_main_result.py is missing from figure-source discovery",
    )


def test_manuscript_references_have_labels():
    assert manuscript_reference_gaps() == ()


def test_manuscript_reference_contract_reports_undefined_labels():
    assert manuscript_reference_gaps(
        paper_text=(
            r"Figure~\ref{fig:defined} and Table~\ref{tab:missing}."
            r"\label{fig:defined}"
        ),
    ) == (
        "tab:missing is referenced but not defined",
    )


def test_source_dependency_pin_gaps_reports_an_unpinned_direct_import():
    gaps = source_dependency_pin_gaps(
        requirements={"numpy": "2.0.2", "matplotlib": "3.9.4"}
    )

    assert gaps == ("pandas -> pandas",)


def test_source_dependency_pin_gaps_reports_missing_distribution_mapping(tmp_path: Path):
    source = tmp_path / "runner.py"
    source.write_text("import mystery_package\n", encoding="utf-8")

    assert source_dependency_pin_gaps(path=source, requirements={}) == (
        "mystery_package has no distribution mapping",
    )
