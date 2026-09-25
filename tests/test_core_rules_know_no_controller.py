"""2026-09-25: Plan A left two controller edges in core (ruling R3's residue).

`rule_held_column` imported `valid_desk_bursts`, and `own_rule_providers`
spelled "smc-pad" and "tablet_desk" inside `checks/`. A show with neither
controller still ran desk code on every check. Ruling P18 also forbids a core
rule reaching `..controllers` or a `..desk*` module directly (level-2 relative
imports), not only the level-1 imports inside `checks/` itself.
"""

import ast
from pathlib import Path

from qlctool.checks.declared_rule_providers import declared_rule_providers
from qlctool.checks.rule_providers import rule_providers
from qlctool.controllers.tablet_desk_rules import TABLET_DESK_RULES

CHECKS = Path(__file__).resolve().parents[1] / "qlctool" / "checks"
CONTROLLER_MODULES = {
    "valid_desk_bursts",
    "rule_desk_bursts",
    "desk_burst_errors",
    "pad_bindings",
    "rule_pad_input",
}


def _reaches_a_controller_package(top_level: str) -> bool:
    return top_level == "controllers" or top_level.startswith("desk")


def _module_imports(tree: ast.Module) -> tuple[set[str], set[str]]:
    """A module's own level-1 imports, and any level-2 import that reaches a controller."""
    level_one: set[str] = set()
    forbidden: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        if node.level == 1:
            level_one.add(node.module.split(".")[-1])
        elif node.level == 2 and _reaches_a_controller_package(node.module.split(".")[0]):
            forbidden.add(node.module)
    return level_one, forbidden


def test_no_core_rule_reaches_a_controller_module():
    seen: set[str] = set()
    forbidden_by_module: dict[str, set[str]] = {}
    pending = ["check_workspace"]
    while pending:
        module = pending.pop()
        if module in seen or not (CHECKS / f"{module}.py").exists():
            continue
        seen.add(module)
        tree = ast.parse((CHECKS / f"{module}.py").read_text(encoding="utf-8"))
        level_one, forbidden = _module_imports(tree)
        if forbidden:
            forbidden_by_module[module] = forbidden
        pending += level_one - {"rule_providers"}
    assert not seen & CONTROLLER_MODULES
    assert not forbidden_by_module


def test_checks_spell_no_provider_name():
    for source in CHECKS.glob("*.py"):
        text = source.read_text(encoding="utf-8")
        assert '"smc-pad"' not in text and '"tablet_desk"' not in text, source.name


def test_the_declared_providers_are_the_installed_ones():
    assert set(declared_rule_providers()) == {"smc-pad", "tablet_desk"}
    assert set(declared_rule_providers()) <= {p.name for p in rule_providers()}


def test_a_wheel_install_declares_nothing(tmp_path):
    assert declared_rule_providers(tmp_path) == ()


def test_the_desk_vouches_for_its_bursts_through_its_provider():
    assert TABLET_DESK_RULES.bounded_latches.__name__ == "tablet_desk_bounded_latches"
