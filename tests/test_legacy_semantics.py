from pathlib import Path

import pytest

from scripts.legacy_division_contract import inspect_contract


def test_default_division_gate_preserves_legacy_formula():
    contract = inspect_contract(Path("tumor_ca.py"))

    assert contract["default_rate"] == 4.0
    assert contract["gate_scale"] == 0.8
    assert contract["default_threshold"] == pytest.approx(3.2)
    assert contract["threshold_in_unit_interval"] is False


def test_calibration_probe_reports_memo_rates_and_saturation():
    contract = inspect_contract(Path("tumor_ca.py"))

    assert contract["calibration_thresholds"] == [
        {
            "raw_rate": 0.5,
            "gate_threshold": pytest.approx(0.4),
            "threshold_in_unit_interval": True,
            "saturates_uniform_gate": False,
        },
        {
            "raw_rate": 1.0,
            "gate_threshold": pytest.approx(0.8),
            "threshold_in_unit_interval": True,
            "saturates_uniform_gate": False,
        },
        {
            "raw_rate": 1.25,
            "gate_threshold": pytest.approx(1.0),
            "threshold_in_unit_interval": True,
            "saturates_uniform_gate": True,
        },
        {
            "raw_rate": 4.0,
            "gate_threshold": pytest.approx(3.2),
            "threshold_in_unit_interval": False,
            "saturates_uniform_gate": True,
        },
    ]

    assert contract["saturation"] == {
        "draw_interval": "[0, 1)",
        "comparison": "draw < gate_threshold",
        "threshold_boundary": 1.0,
        "raw_rate_boundary": pytest.approx(1.25),
        "saturates_when": "gate_threshold >= 1.0",
        "saturating_raw_rates": [1.25, 4.0],
        "behavior": (
            "Every eligible cell passes this gate at or above the raw-rate "
            "boundary 1.25; rates above that boundary are indistinguishable "
            "to this gate."
        ),
    }


def test_calibration_probe_preserves_exact_owner_decision_boundary():
    boundary = inspect_contract(Path("tumor_ca.py"))["owner_decision_boundary"]

    assert boundary == {
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


def test_contract_rejects_a_clamped_or_non_multiplicative_gate(tmp_path: Path):
    source = Path("tumor_ca.py").read_text(encoding="utf-8")
    source = source.replace(
        "division_prob = self.local_division_rate * 0.8",
        "division_prob = np.minimum(self.local_division_rate * 0.8, 1.0)",
    )
    candidate = tmp_path / "tumor_ca.py"
    candidate.write_text(source, encoding="utf-8")

    with pytest.raises(ValueError, match="division_prob must remain an explicit multiplication"):
        inspect_contract(candidate)


def test_contract_rejects_boolean_numeric_multipliers(tmp_path: Path):
    source = Path("tumor_ca.py").read_text(encoding="utf-8")
    source = source.replace(
        "division_prob = self.local_division_rate * 0.8",
        "division_prob = self.local_division_rate * True",
    )
    candidate = tmp_path / "tumor_ca.py"
    candidate.write_text(source, encoding="utf-8")

    with pytest.raises(ValueError, match="division_prob must use a numeric scalar multiplier"):
        inspect_contract(candidate)
