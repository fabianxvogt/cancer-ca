"""Regression contract for the bounded division-semantics audit."""

from __future__ import annotations

import json

from scripts.division_semantics_sensitivity import (
    EXPECTED_DIFFERENT_CELLS,
    EXPECTED_RESULTS_SHA256,
    main,
)


def test_executable_emits_the_validated_fixture(capsys) -> None:
    main()

    payload = json.loads(capsys.readouterr().out)
    assert payload["scope"]["result_fixture_sha256"] == EXPECTED_RESULTS_SHA256
    assert {
        name: row["different_cells"] for name, row in payload["comparisons"].items()
    } == EXPECTED_DIFFERENT_CELLS
    assert payload["replay"] == {
        "bernoulli_screen": {
            "final_grid_equal": True,
            "summary_equal": True,
            "trajectory_equal": True,
        },
        "legacy": {
            "final_grid_equal": True,
            "summary_equal": True,
            "trajectory_equal": True,
        },
    }
    assert payload["results"]["legacy"]["Adaptive Low"]["therapy_step_counts"] == {
        "0.000": 80,
        "0.125": 86,
        "0.250": 14,
    }
    assert payload["results"]["bernoulli_screen"]["Adaptive Low"][
        "therapy_step_counts"
    ] == {"0.000": 80, "0.125": 88, "0.250": 12}
