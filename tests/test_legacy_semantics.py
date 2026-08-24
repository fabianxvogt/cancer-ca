from pathlib import Path

import pytest

from scripts.legacy_division_contract import inspect_contract


def test_default_division_gate_preserves_legacy_formula():
    contract = inspect_contract(Path("tumor_ca.py"))

    assert contract["default_rate"] == 4.0
    assert contract["gate_scale"] == 0.8
    assert contract["default_threshold"] == pytest.approx(3.2)
    assert contract["threshold_in_unit_interval"] is False


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
