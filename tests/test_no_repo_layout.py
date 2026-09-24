"""Spec step 6: nothing in the package may assume where this repository keeps its files."""

import ast
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "qlctool"
REPO_FOLDERS = ("QLC+ Fixtures", "QLC+ Setups", "QLC+ InputProfiles")


def _docstrings(tree: ast.AST) -> set[int]:
    return {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }


def test_no_source_names_a_repo_folder_or_climbs_to_the_repo():
    offenders = []
    for source in sorted(PACKAGE.rglob("*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        skip = _docstrings(tree)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and id(node) not in skip
                and any(folder in node.value for folder in REPO_FOLDERS)
            ):
                offenders.append(f"{source.name}:{node.lineno} {node.value!r}")
            if (
                isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Attribute)
                and node.value.attr == "parents"
                and isinstance(node.slice, ast.Constant)
                and node.slice.value >= 3
            ):
                offenders.append(f"{source.name}:{node.lineno} parents[{node.slice.value}]")
    assert offenders == []
