"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers heads running their own programme, the
vertical smoke columns' latching, and a fixture definition declaring too few
heads for its colour rings.
"""

import re

import pytest
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show
from rig_root import RIG_ROOT

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.group_fixtures import group_fixtures
from qlctool.checks.lit import lit
from qlctool.checks.reach import reach
from qlctool.checks.room_states import room_states
from qlctool.checks.rule_undeclared_heads import check_undeclared_heads
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.iter_local import iter_local
from qlctool.localname import localname

REPO = RIG_ROOT
SHOWS = ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw")


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def test_a_head_nothing_takes_off_its_own_programme(library):
    """2026-08-30, the two MAC WASH 1915Z on their first night: "se quedaban
    mirando para abajo y hacian cosas raras como una especie de cambios de
    colores muy rapidos".

    The movement was aimed at the measured audience window and the colour was
    a wheel stepping every eight beats, so what the room saw was not the show
    at all: the fixture was running itself. Its `Function Mode` channel is one
    blanket 000-255 range - nothing for `rule_internal_program` to match on -
    and no function in the show wrote it, so it kept whatever the last
    controller left there. Take the parked value back out and the rule must
    bite.
    """
    workspace = _show()
    capabilities = {
        capability.fixture.fixture_id: capability
        for capability in capabilities_of(workspace.root, library)
    }
    victims = {
        fixture_id: capability.offsets_for_role(roles.EFFECT)
        for fixture_id, capability in capabilities.items()
        if capability.has_role(roles.EFFECT)
        and capability.has_role(roles.PAN)
        and capability.has_role(roles.RED)
    }
    assert victims, "no RGB moving head in the show carries a mode channel"

    stripped = 0
    for function in find_local(workspace.root, "Engine"):
        for element in findall_local(function, "FixtureVal"):
            offsets = victims.get(int(element.attrib.get("ID", -1)))
            if not offsets or not element.text:
                continue
            numbers = [int(n) for n in element.text.split(",") if n != ""]
            kept = [
                (channel, value)
                for channel, value in zip(numbers[::2], numbers[1::2], strict=True)
                if channel not in offsets
            ]
            if len(kept) * 2 != len(numbers):
                stripped += 1
            element.text = ",".join(str(n) for pair in kept for n in pair)
    assert stripped, "the show never parked the mode channel to begin with"

    findings = [f for f in check_workspace(workspace, library) if f.rule == "modo sin dueño"]
    assert findings, "a head left running its own programme went unnoticed"
    assert any(
        capabilities[fixture_id].fixture.name in f.fixtures
        for f in findings
        for fixture_id in victims
    )


def test_a_smoke_column_a_latched_button_can_fire(library):
    """2026-08-30: "el humo vertical nunca debe dispararse solo" (owner).

    The four vertical machines fire a lit column and empty a tank doing it,
    which is why their button is a Flash and their pump is in the group QLC+
    resets every cycle. Neither helps if the same scene is reachable from a
    button that latches - AUTO, a level, a Toggle - so the wiring is the rule:
    turn the column's own button into a Toggle and it must bite.
    """
    workspace = _show()
    console = find_local(workspace.root, "VirtualConsole")
    switched = 0
    for button in iter_local(console, "Button"):
        if "HUMO VERT ·" not in (button.attrib.get("Caption") or ""):
            continue
        action = find_local(button, "Action")
        assert action is not None and action.text == "Flash"
        action.text = "Toggle"
        switched += 1
    assert switched, "the console lost its vertical smoke button"

    findings = [f for f in check_workspace(workspace, library) if f.rule == "columna automatica"]
    assert findings, "a latched smoke column went unnoticed"
    assert any("Humo Vertical" in fixture for f in findings for fixture in f.fixtures)


def test_one_wheel_step_cannot_switch_the_strobe_off_for_all_of_them(library):
    """2026-08-28, from the Codex review of `estrobo pegado`: the rule merged
    the reach of everything hanging off a state, so a strobe-off written under
    one alternative read as though it were written under all of them.

    A chaser's steps are not concurrent - they are different rooms, one at a
    time. Reproduced by leaving the panels' strobe-off in a single step of
    `Ciclo Paneles` and taking it out of everywhere else: AUTO's merged reach
    still finds a strobe-off, which is what made the old rule pass, while the
    room spends the other 41 steps latched.
    """
    workspace = _show()
    panels = {24, 25, 27, 28}
    # The two states that are a Scene themselves keep theirs, so that under the
    # old merged reach every lit state still had an owner and the rule was
    # silent - which is what this test is here to break.
    kept = {"Paneles - Effect 1", "Blanco Total", "Intensidad Charla Pixeles"}
    stripped = 0
    for name, function in _functions(workspace).items():
        if function.attrib.get("Type") != "Scene" or name in kept:
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) not in panels or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            if pairs.get(4) == 0:  # channel 5 is the strobe; leave the
                pairs.pop(4)  # flash scenes' own strobing value alone
                stripped += 1
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))
    assert stripped, "the repro changed nothing; the scene shape moved"

    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    states = room_states(workspace.root, graph, groups)
    merged = {state_id: reach(graph, groups, state_id).get(24, {}) for state_id in states}
    assert all(4 in written for written in merged.values() if lit(written.get(0, 0))), (
        "the old merged reach would have caught this on its own; repro too broad"
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "estrobo pegado"]

    assert findings, (
        "a strobe-off surviving in one wheel step masked every step that lost "
        "it - the union is back"
    )
    assert any("WX-60WPS" in fixture for f in findings for fixture in f.fixtures)


def test_a_fixture_with_three_rings_and_one_head_is_caught(tmp_path):
    """2026-08-31: the two MAC WASH 1915Z were about to be put in a fixture
    group so they would finally get a colour bank and a matrix. Their 23-channel
    mode has `Red/Green/Blue ring 1..3` and declared no `<Head>` at all.

    QLC+ does not read that as "no heads": it builds one head holding every
    channel, and that head keeps only the last channel of each colour. A matrix
    would have painted the outer ring and left the other two holding whatever
    was written last - the panels' bug, on part of a fixture. Reproduced by
    taking the heads back out of the definition.
    """
    for qxf in (REPO / "QLC+ Fixtures").glob("*.qxf"):
        text = qxf.read_text(encoding="utf-8")
        if qxf.name.startswith("Mac-Mah-MAC-WASH"):
            text = re.sub(r" *<Head>.*?</Head>\n", "", text, flags=re.S)
            assert "<Head>" not in text
        (tmp_path / qxf.name).write_text(text, encoding="utf-8")
    headless = FixtureLibrary.load([tmp_path])

    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show()
    group = next(
        element
        for element in workspace.root.iter()
        if localname(element) == "FixtureGroup"
        and (find_local(element, "Name").text or "") == "Cabezas"
    )
    size = find_local(group, "Size")
    size.set("X", str(int(size.attrib["X"]) + 2))
    for cell, fixture_id in enumerate((41, 42)):
        head = etree.SubElement(group, f"{{{QLC_NS}}}Head")
        head.set("X", str(int(size.attrib["X"]) - 2 + cell))
        head.set("Y", "0")
        head.set("Fixture", str(fixture_id))
        head.text = "0"

    findings = [f for f in check_workspace(workspace, headless) if f.rule == "cabezas sin declarar"]

    assert findings, "a fixture offering a matrix one of its three rings went unnoticed"
    assert any("MAC WASH" in fixture for f in findings for fixture in f.fixtures)


def test_the_shipped_definitions_declare_a_head_per_colour_set(library):
    """The other half of the rule: every fixture the show patches must already
    satisfy it, or the rule is only true of the one file it was written for."""
    for name in SHOWS:
        workspace = _show(name)
        graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
        assert not check_undeclared_heads(graph, workspace.root)


def test_three_empty_head_blocks_do_not_satisfy_the_rule(tmp_path):
    """Found in review, 2026-08-31: counting `<Head>` elements is not the same
    as counting heads that hold a colour. Three blocks listing the pan and tilt
    channels satisfy a count and leave the matrix exactly as broken."""
    for qxf in (REPO / "QLC+ Fixtures").glob("*.qxf"):
        text = qxf.read_text(encoding="utf-8")
        if qxf.name.startswith("Mac-Mah-MAC-WASH"):
            text = re.sub(
                r"( *<Head>\n)(?: *<Channel>\d+</Channel>\n)+",
                r"\1   <Channel>0</Channel>\n   <Channel>2</Channel>\n",
                text,
            )
            assert text.count("<Head>") == 3
        (tmp_path / qxf.name).write_text(text, encoding="utf-8")
    colourless = FixtureLibrary.load([tmp_path])

    workspace = _show()
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, colourless))

    findings = check_undeclared_heads(graph, workspace.root)

    assert findings, "three heads holding no colour passed the head count"
    assert any("MAC WASH" in fixture for f in findings for fixture in f.fixtures)
