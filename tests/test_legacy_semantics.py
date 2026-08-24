import ast
from pathlib import Path


def test_default_division_gate_preserves_legacy_formula():
    tree = ast.parse(Path("tumor_ca.py").read_text(encoding="utf-8"))
    assignments = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name):
            assignments[target.id] = node.value
        elif isinstance(target, ast.Attribute):
            assignments[target.attr] = node.value

    default_rate = ast.unparse(assignments["local_division_rate"])
    division_gate = ast.unparse(assignments["division_prob"])

    assert "4.0" in default_rate
    assert division_gate == "self.local_division_rate * 0.8"
