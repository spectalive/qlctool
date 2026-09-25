"""Every finding message comes from the catalogue, never from a literal (ruling B10, round 2).

2026-09-25: round 1 named the rules in the workspace's language, and the
round-1 review found that a `Finding("nueva regla", ...)` with a literal
passed the drift test. Round 2 moved the 93 Spanish message templates into
`[findings]`. This scan keeps them there: every `Finding(...)` in
`qlctool/checks/` names its rule by a `*RULE_ID` constant and its message by
a `[findings]` identifier, both by keyword, and no string that reaches a
finding carries a word only the Spanish catalogue uses.
"""

import ast
import re
from pathlib import Path

import pytest

from qlctool.checks.promise_words import PROMISE_WORDS
from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.shipped_languages import shipped_languages
from qlctool.names.template_fields import template_fields

CHECKS = Path(__file__).resolve().parents[1] / "qlctool" / "checks"
WORD = r"[^\W\d_]{4,}"
# The units that render a finding's own identifier, which is not a literal there.
RENDERERS = {"finding.py", "named_findings.py"}


def _calls(name: str) -> list[tuple[str, ast.Call]]:
    """Every `name(...)` call in `qlctool/checks/`, with the module it is in."""
    found = []
    for module in sorted(CHECKS.glob("*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        found += [
            (module.name, node)
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == name
        ]
    return found


def _keyword(call: ast.Call, name: str) -> ast.expr | None:
    return next((k.value for k in call.keywords if k.arg == name), None)


def _spanish_only_words() -> set[str]:
    """Words of the Spanish `[findings]` entries that the English twin does not use."""
    spanish, english = load_catalogue("es")["findings"], load_catalogue("en")["findings"]
    words: set[str] = set()
    for identifier, text in spanish.items():
        same = set(re.findall(WORD, english[identifier]))
        words |= {w for w in re.findall(WORD, text) if w not in same}
    return words


def _strings(node: ast.AST, skip: ast.AST | None = None) -> list[str]:
    """Every string literal under `node`, f-string parts included, except `skip`'s."""
    return [
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str) and child is not skip
    ]


def test_the_scan_sees_every_finding():
    assert len(_calls("Finding")) >= 76


def test_every_finding_names_its_rule_and_message_by_keyword():
    offenders = []
    for module, call in _calls("Finding"):
        rule_id = _keyword(call, "rule_id")
        if call.args or _keyword(call, "message") is not None:
            offenders.append(f"{module}:{call.lineno} passes a positional or a message")
        if not (isinstance(rule_id, ast.Name) and rule_id.id.endswith("RULE_ID")):
            offenders.append(f"{module}:{call.lineno} rule_id is not a *RULE_ID constant")
        if _keyword(call, "message_id") is None:
            offenders.append(f"{module}:{call.lineno} has no message_id")
    assert offenders == []


def _message_ids(call: ast.Call) -> list[str]:
    """The identifiers a Finding names directly: a literal, or either arm of a choice."""
    value = _keyword(call, "message_id")
    arms = (value.body, value.orelse) if isinstance(value, ast.IfExp) else (value,)
    return [arm.value for arm in arms if isinstance(arm, ast.Constant)]


def _findings_identifiers() -> dict[str, str]:
    """Every identifier `qlctool/checks/` hands a finding or a phrase -> where it is."""
    used: dict[str, str] = {}
    for module, call in _calls("Finding"):
        for identifier in _message_ids(call):
            used[identifier] = f"{module}:{call.lineno}"
    for module, call in _calls("Phrase"):
        if module in RENDERERS:
            continue
        first = call.args[0] if call.args else _keyword(call, "message_id")
        if isinstance(first, ast.Subscript) and ast.unparse(first.value) == "PROMISE_WORDS":
            continue
        assert isinstance(first, ast.Constant), f"{module}:{call.lineno} names no literal"
        used[first.value] = f"{module}:{call.lineno}"
    # The caption promise names its words through this table.
    used |= dict.fromkeys(PROMISE_WORDS.values(), "promise_words.py")
    return used


@pytest.mark.parametrize("language", shipped_languages())
def test_every_message_identifier_is_in_the_catalogue(language):
    catalogue = load_catalogue(language)
    everywhere = {identifier for section in catalogue.values() for identifier in section}
    used = _findings_identifiers()
    assert sorted(i for i in used if i not in everywhere) == []
    # A message a finding names directly is a [findings] entry, not a caption.
    direct = {identifier for _, call in _calls("Finding") for identifier in _message_ids(call)}
    assert sorted(direct - set(catalogue["findings"])) == []
    # An entry nothing names is a message that was removed or renamed.
    assert sorted(set(catalogue["findings"]) - set(used)) == []


def test_no_spanish_word_reaches_a_finding_from_code():
    words = _spanish_only_words()
    leaks = []
    for name in ("Finding", "Phrase", "Joined"):
        for module, call in _calls(name):
            identifier = _keyword(call, "message_id") or (call.args[0] if call.args else None)
            for text in _strings(call, skip=identifier):
                hits = sorted(w for w in re.findall(WORD, text) if w in words)
                if hits:
                    leaks.append(f"{module}:{call.lineno} {text!r}: {hits}")
    assert leaks == []


# Literals in `qlctool/checks/` that spell a Spanish-only word and never reach
# a finding: the family key `family_frames` reads roles by.
NEVER_SAID = {("family_frames.py", "color")}


def _docstrings(tree: ast.Module) -> set[int]:
    """The ids of the module's, classes' and functions' docstring constants."""
    kinds = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    return {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, kinds)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }


def test_no_spanish_word_is_spelled_anywhere_in_the_checks():
    """Review of B10 round 2 (2026-09-26): the call-site scan missed a helper.

    `rule_grid_order._where` returning "sin colgar" builds the literal outside
    the `Joined(...)` that carries it, so only a scan of every string in the
    module sees it; "colgar" is a word only the Spanish catalogue uses.
    """
    words = _spanish_only_words()
    identifiers = {i for section in load_catalogue("es").values() for i in section}
    leaks = []
    for module in sorted(CHECKS.glob("*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        docstrings = _docstrings(tree)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                continue
            if id(node) in docstrings or node.value in identifiers:
                continue
            if (module.name, node.value) in NEVER_SAID:
                continue
            hits = sorted(w for w in re.findall(WORD, node.value) if w in words)
            if hits:
                leaks.append(f"{module.name}:{node.lineno} {node.value!r}: {hits}")
    assert leaks == []


def test_the_wide_scan_would_see_sin_colgar():
    assert "colgar" in _spanish_only_words()


def test_every_spanish_entry_has_an_english_twin_with_the_same_fields():
    spanish, english = load_catalogue("es")["findings"], load_catalogue("en")["findings"]
    assert list(spanish) == list(english)
    for identifier, text in spanish.items():
        assert sorted(template_fields(english[identifier])) == sorted(template_fields(text)), (
            identifier
        )


def test_the_engine_literals_stay_in_both_languages():
    """Engine calls, QLC+ log lines, the CLI command and "7R" are not translated."""
    literals = {
        "flash_scene_not_a_scene": "Scene::flash",
        "state_proxy_starts_state": "qmlui VCButton::slotFunctionRunning",
        "tap_dial_same_multiplier": "VCSpeedDial::applyFunctionsTime",
        "tempo_units_beats_fade": "EFX::loopDuration",
        "tap_dial_no_functions": "«Unknown speed dial tag: ControlBPM»",
        "tempo_units_collection_tempo": "«Unknown collection tag: Tempo»",
        "grid_order_row_jumps": "`qlctool patch --group-sort {group}`",
        "shutter_endpoint_half_open": "7R",
        "unaimed_movement_mid_tilt": "7R",
    }
    for language in shipped_languages():
        findings = load_catalogue(language)["findings"]
        assert {i: t for i, t in literals.items() if t not in findings[i]} == {}, language


def test_the_spanish_messages_are_the_ones_vibra_has_always_printed():
    spanish = load_catalogue("es")["findings"]
    assert spanish["console_same_key"] == "comparten la tecla «{key}»: pulsarla dispara todos"
    assert spanish["family_owner_no_toggle"].startswith("no tiene su Toggle en el marco")
    assert spanish["promise_gobo"] == "rueda de gobos"
