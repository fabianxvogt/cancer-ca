"""Focused tests for the dependency-aware structural smoke contract."""

import pytest

from scripts.smoke_core_experiment import (
    EXPECTED_HISTORY_KEYS,
    EXPECTED_STRATEGIES,
    THERAPY_START,
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
