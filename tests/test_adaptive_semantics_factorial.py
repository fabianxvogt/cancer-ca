"""Regression contract for the Adaptive semantics × cutoff factorial audit."""

from __future__ import annotations

from hashlib import sha256
import json

import pytest

from scripts.adaptive_semantics_factorial import main


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
        for seed in (41, 42, 43)
        for semantic in ("legacy", "unit_interval")
    },
}


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def _metric(row: dict, name: str) -> float | int:
    if name == "stability_score":
        return row["stability"]["stability_score"]
    return row[name]


def test_factorial_executable_emits_validated_seed_level_fixture(capsys) -> None:
    main()

    payload = json.loads(capsys.readouterr().out)
    fixture = {
        name: payload[name]
        for name in (
            "closed_loop",
            "cross_yoked",
            "decompositions",
            "execution_summary",
        )
    }
    assert payload["scope"]["fixture_sha256"] == EXPECTED_FIXTURE_SHA256
    assert _canonical_digest(fixture) == EXPECTED_FIXTURE_SHA256
    assert payload["classification"] == (
        "INCREMENTAL / EMPIRICAL bounded software-model audit"
    )
    assert payload["scope"]["biological_or_clinical_claim"] is False
    assert payload["scope"]["size"] == 24
    assert payload["scope"]["steps"] == 180
    assert payload["scope"]["seeds"] == [41, 42, 43]
    assert payload["scope"]["semantics"] == {
        "legacy": 4.0,
        "unit_interval": 1.0,
    }
    assert payload["scope"]["cutoffs"] == {
        "unscaled": 500,
        "capacity_scaled": 20,
    }
    assert payload["scope"]["core_cutoff_fraction"] == 500 / (120 * 120)
    assert payload["scope"]["scaled_cutoff_fraction"] == 20 / (24 * 24)
    assert payload["scope"]["therapy_window_steps"] == {
        "start_inclusive": 25,
        "end_exclusive": 125,
    }
    assert payload["scope"]["response_history_indices"] == {
        "pretherapy_baseline": 24,
        "inherited_post_first_dose_baseline": 25,
        "nadir_start_inclusive": 25,
        "nadir_stop_exclusive": 145,
    }
    assert {
        key: row["high_dose_steps"] for key, row in payload["closed_loop"].items()
    } == EXPECTED_HIGH_DOSE_STEPS
    assert len(payload["closed_loop"]) == 12
    assert len(payload["cross_yoked"]) == 12
    assert len(payload["decompositions"]) == 6
    assert payload["execution_summary"] == {
        "closed_loop_executions": 12,
        "cross_yoked_executions": 12,
        "total_executions": 24,
        "unique_tumor_trajectories": 16,
        "unique_dose_paths": 4,
        "exact_closed_loop_replays": 8,
    }

    all_rows = {**payload["closed_loop"], **payload["cross_yoked"]}
    assert len({row["tumor_trajectory_sha256"] for row in all_rows.values()}) == 16
    assert len({row["dose_sha256"] for row in all_rows.values()}) == 4
    exact_closed_loop_replays = 0
    for row in all_rows.values():
        assert "response_pct" not in row
        doses = row["dose_path"]
        assert len(doses) == 180
        assert doses[:25] == [0.0] * 25
        assert doses[125:] == [0.0] * 55
        assert set(doses[25:125]) <= {0.125, 0.25}
        assert row["high_dose_steps"] + row["low_dose_steps"] == 100
        assert row["cumulative_exposure"] == pytest.approx(sum(doses))
        assert row["response_pretherapy_pct"] == pytest.approx(
            (row["pretherapy_baseline_tumor"] - row["nadir"])
            / (row["pretherapy_baseline_tumor"] + 1)
            * 100
        )
        assert row["response_inherited_post_first_dose_pct"] == pytest.approx(
            (row["post_first_dose_baseline_tumor"] - row["nadir"])
            / (row["post_first_dose_baseline_tumor"] + 1)
            * 100
        )

    for seed in (41, 42, 43):
        for cutoff in ("unscaled", "capacity_scaled"):
            for target, source in (
                ("unit_interval", "legacy"),
                ("legacy", "unit_interval"),
            ):
                cross = payload["cross_yoked"][
                    f"{seed}:target={target}:path={source}:{cutoff}"
                ]
                source_closed = payload["closed_loop"][f"{seed}:{source}:{cutoff}"]
                target_closed = payload["closed_loop"][f"{seed}:{target}:{cutoff}"]
                assert cross["dose_path"] == source_closed["dose_path"]
                assert cross["dose_sha256"] == source_closed["dose_sha256"]
                if (
                    cross["dose_sha256"] == target_closed["dose_sha256"]
                    and cross["tumor_trajectory_sha256"]
                    == target_closed["tumor_trajectory_sha256"]
                    and cross["final_grid_sha256"] == target_closed["final_grid_sha256"]
                ):
                    exact_closed_loop_replays += 1

    assert exact_closed_loop_replays == 8

    for seed in (41, 42, 43):
        legacy = payload["closed_loop"][f"{seed}:legacy:capacity_scaled"]
        unit = payload["closed_loop"][f"{seed}:unit_interval:capacity_scaled"]
        assert legacy["dose_path"] == unit["dose_path"]
        assert legacy["high_dose_steps"] == 100
        assert legacy["low_dose_steps"] == 0

    metric_names = (
        "response_pretherapy_pct",
        "response_inherited_post_first_dose_pct",
        "final_tumor_burden",
        "active_tumor_auc",
        "final_resistant",
        "stability_score",
    )
    for seed in (41, 42, 43):
        for cutoff in ("unscaled", "capacity_scaled"):
            legacy = payload["closed_loop"][f"{seed}:legacy:{cutoff}"]
            unit = payload["closed_loop"][f"{seed}:unit_interval:{cutoff}"]
            unit_on_legacy = payload["cross_yoked"][
                f"{seed}:target=unit_interval:path=legacy:{cutoff}"
            ]
            legacy_on_unit = payload["cross_yoked"][
                f"{seed}:target=legacy:path=unit_interval:{cutoff}"
            ]
            rows = payload["decompositions"][f"{seed}:{cutoff}"]
            for metric_name in metric_names:
                row = rows[metric_name]
                ll = _metric(legacy, metric_name)
                uu = _metric(unit, metric_name)
                ul = _metric(unit_on_legacy, metric_name)
                lu = _metric(legacy_on_unit, metric_name)
                assert row["total_semantics"] == uu - ll
                assert row["semantics_on_legacy_path"] == ul - ll
                assert row["unit_path_substitution"] == uu - ul
                assert row["legacy_path_substitution"] == lu - ll
                assert row["semantics_on_unit_path"] == uu - lu
                assert row["total_semantics"] == pytest.approx(
                    row["semantics_on_legacy_path"] + row["unit_path_substitution"],
                    rel=0,
                    abs=1e-12,
                )
                assert row["total_semantics"] == pytest.approx(
                    row["legacy_path_substitution"] + row["semantics_on_unit_path"],
                    rel=0,
                    abs=1e-12,
                )

    expected_scaled_pretherapy_contrasts = {
        41: -2.946274,
        42: 12.651646,
        43: 0.519931,
    }
    for seed, expected in expected_scaled_pretherapy_contrasts.items():
        observed = payload["decompositions"][f"{seed}:capacity_scaled"][
            "response_pretherapy_pct"
        ]["total_semantics"]
        assert observed == pytest.approx(expected, abs=5e-7)

    expected_scaled_inherited_contrasts = {
        41: -2.982456,
        42: 12.902857,
        43: 0.355481,
    }
    for seed, expected in expected_scaled_inherited_contrasts.items():
        observed = payload["decompositions"][f"{seed}:capacity_scaled"][
            "response_inherited_post_first_dose_pct"
        ]["total_semantics"]
        assert observed == pytest.approx(expected, abs=5e-7)

    seed_42_unscaled_pretherapy = payload["decompositions"]["42:unscaled"][
        "response_pretherapy_pct"
    ]
    assert seed_42_unscaled_pretherapy["total_semantics"] == pytest.approx(
        14.038128, abs=5e-7
    )
    assert seed_42_unscaled_pretherapy["semantics_on_legacy_path"] == pytest.approx(
        14.384749, abs=5e-7
    )
    assert seed_42_unscaled_pretherapy["unit_path_substitution"] == pytest.approx(
        -0.346620, abs=5e-7
    )

    seed_42_unscaled_inherited = payload["decompositions"]["42:unscaled"][
        "response_inherited_post_first_dose_pct"
    ]
    assert seed_42_unscaled_inherited["total_semantics"] == pytest.approx(
        14.320590, abs=5e-7
    )
    assert seed_42_unscaled_inherited["semantics_on_legacy_path"] == pytest.approx(
        14.672083, abs=5e-7
    )
    assert seed_42_unscaled_inherited["unit_path_substitution"] == pytest.approx(
        -0.351494, abs=5e-7
    )
