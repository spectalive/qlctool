"""Every check rule is named by the catalogue, never by a literal (ruling B10, 2026-09-25).

A rule module states its English identifier (`RULE_ID`, or `<KIND>_RULE_ID`
for a second rule in the same module); what a person reads is the `[checks]`
entry of the workspace's language. A module that went back to a Spanish
`RULE = "..."`, or an identifier missing from a catalogue, would print Spanish
in an English show or fail at the first finding.
"""

import re
from pathlib import Path

import pytest

from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.shipped_languages import shipped_languages

CHECKS = Path(__file__).resolve().parents[1] / "qlctool" / "checks"
LITERAL_RULE = re.compile(r"^\w*RULE\s*=", re.M)
RULE_ID = re.compile(r'^\w*RULE_ID\s*=\s*"([^"]*)"', re.M)


def _modules() -> list[Path]:
    return sorted(CHECKS.glob("rule_*.py"))


def _identifiers() -> dict[str, str]:
    """Identifier -> the module that declares it."""
    found: dict[str, str] = {}
    for module in _modules():
        for identifier in RULE_ID.findall(module.read_text(encoding="utf-8")):
            assert identifier not in found, f"{identifier} in {module.name} and {found[identifier]}"
            found[identifier] = module.name
    return found


def test_no_rule_module_names_its_rule_with_a_literal():
    offenders = [m.name for m in _modules() if LITERAL_RULE.search(m.read_text(encoding="utf-8"))]
    assert offenders == []


def test_the_rule_modules_declare_identifiers():
    assert len(_identifiers()) >= 67


@pytest.mark.parametrize("language", shipped_languages())
def test_every_rule_identifier_is_named_in_every_catalogue(language):
    catalogued = load_catalogue(language)["checks"]
    assert sorted(set(_identifiers()) - set(catalogued)) == []
    # A catalogue entry no module declares is a rule that was removed or renamed.
    assert sorted(set(catalogued) - set(_identifiers())) == []


def test_the_spanish_names_are_the_ones_vibra_has_always_printed():
    spanish = load_catalogue("es")["checks"]
    assert spanish["empty_frame"] == "marco vacio"
    assert spanish["missing_fixture_definition"] == "sin definicion"
    assert spanish["family_owner"] == "familia con dueño"
