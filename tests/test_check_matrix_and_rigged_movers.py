"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers the 2026-09-26/27 en-sala DMX audit -
a matrix drawn over a group nobody can see, rigged movers left unaimed, a
fan folded back into patch order, a figure owing movement to a spare head,
and a two-Scene Collection still counting as a wrapper pick.
"""

import copy

import pytest
from efx_under import efx_under as _efx_under
from fixture_val_pairs import fixture_val_pairs as _pairs_of
from functions_by_id_of_workspace import functions_by_id_of_workspace as _functions_by_id
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show
from shipped_graphs import shipped_graphs as _shipped_graphs
from write_fixture_val_pairs import write_fixture_val_pairs as _write_pairs

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.room_states import room_states
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_groups import fixture_groups
from qlctool.fixture_library import FixtureLibrary
from qlctool.iter_local import iter_local


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def test_2026_09_26_a_matrix_nobody_can_see(library):
    """2026-09-26, en-sala DMX audit (items 4 and 12): every `Cabezas` matrix
    left the rigged rig as it was. The group is the four 7R beams - a colour
    wheel, no red, green or blue for a matrix to write - and eight washes the
    stage plot hides as spares, so every cell a matrix could paint was in a
    flight case. Ruling D6: no matrix on such a group. Draw `Cabezas - Fill
    Rojo` back on the group and the rule must name it; leave most of a group's
    colour cells hidden and it warns.
    """
    from qlctool.checks.finding import ERROR, WARNING
    from qlctool.checks.rule_invisible_matrix import RULE_ID, check_invisible_matrix

    for name, graph, _ in _shipped_graphs(library):
        assert check_invisible_matrix(graph, _show(name).root) == [], name

    workspace = _show()
    groups = {group.name: group for group in fixture_groups(workspace.root)}
    source = next(
        f
        for f in iter_local(workspace.root, "Function")
        if f.get("Type") == "RGBMatrix"
        and find_local(f, "FixtureGroup").text == str(groups["PAR"].group_id)
    )
    matrix = copy.deepcopy(source)
    matrix.set("ID", str(1 + max(int(i) for i in _functions_by_id(workspace))))
    matrix.set("Name", "Cabezas - Fill Rojo")
    find_local(matrix, "FixtureGroup").text = str(groups["Cabezas"].group_id)
    source.addnext(matrix)
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [(f.function, f.severity) for f in findings] == [("Cabezas - Fill Rojo", ERROR)]

    workspace = _show("Vibra.qxw")
    par = next(g for g in fixture_groups(workspace.root) if g.name == "PAR")
    hidden = set(par.fixture_ids[:4])
    for item in iter_local(workspace.root, "FxItem"):
        if int(item.get("ID")) in hidden:
            item.set("Hidden", "1")
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert findings
    assert {(f.severity, f.fields["group"], f.fields["spares"]) for f in findings} == {
        (WARNING, "PAR", 5)
    }


def test_2026_09_26_the_macs_left_at_mid_travel(library):
    """2026-09-26, en-sala DMX audit (items 2, 15, 16, concern C4): the two
    MAC WASH sat at 127/127 - the wall behind the stage - through `Beams
    Abanico`, `Beams Cruce`, `Escenario` and `Cabezas Centro`, and waited 10
    and 11.6 s at the start of `Ola Vertical`. Ruling D7: they hold the wash
    window's centre on the beam-only looks until the stage is measured for
    them. Put each cause back - the MACs out of the fan pick, the home scene's
    MAC tilt at mid-travel, the wave Serial again - and the rule must name
    the heads left unaimed.
    """
    from qlctool.checks.rule_unaimed_rigged_mover import RULE_ID, check_unaimed_rigged_mover

    for name, graph, groups in _shipped_graphs(library):
        root = _show(name).root
        states = room_states(root, graph, groups)
        assert check_unaimed_rigged_mover(graph, groups, root, states) == [], name

    macs = ("MAC WASH 1915Z #1", "MAC WASH 1915Z #2")
    workspace = _show("Vibra.qxw")
    by_id = _functions_by_id(workspace)
    pick = _functions(workspace)["Jugar · Beams Abanico"]
    for step in findall_local(pick, "Step"):
        if by_id[step.text].get("Name") != "Beams Abanico":
            pick.remove(step)
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [(f.function, f.fixtures) for f in findings] == [("Jugar · Beams Abanico", macs)]

    workspace = _show("Vibra.qxw")
    caps = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    home = _functions(workspace)["Cabezas Centro"]
    for value in findall_local(home, "FixtureVal"):
        capability = caps[int(value.attrib["ID"])]
        if capability.fixture.name in macs:
            pairs = _pairs_of(value)
            for offset in capability.offsets_for_role(roles.TILT):
                pairs[offset] = 127
            _write_pairs(value, pairs)
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert "Momento Charla" in {f.function for f in findings}
    assert all(f.fixtures == macs for f in findings)

    workspace = _show("Vibra.qxw")
    wave = _efx_under(_functions_by_id(workspace), _functions(workspace)["Ola Vertical Washes"])
    find_local(wave[0], "PropagationMode").text = "Serial"
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert ("Jugar · Ola Vertical", ("MAC WASH 1915Z #2",)) in [
        (f.function, f.fixtures) for f in findings
    ]


def test_2026_09_27_a_fan_folded_in_patch_order(library):
    """2026-09-27, Round 2 review of the en-sala DMX audit: `Beams Abanico`
    spread the four 7R evenly - 62, 75, 89, 102 - in patch order, so across
    the stage (fixtures 20, 22, 23, 21) the pans read 62, 89, 102, 75 and the
    house-right head folded back into the middle; `Beams Cruce` the same,
    reversed. Controller ruling: the fan follows stage order, as `Alternado`
    does (D5). Put the patch-order pans back and the rule must name the fan.
    """
    from qlctool.checks.rule_fan_order import RULE_ID, check_fan_order

    for name, graph, groups in _shipped_graphs(library):
        assert check_fan_order(graph, groups, _show(name).root) == [], name

    workspace = _show("Vibra.qxw")
    caps = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    fan = _functions(workspace)["Beams Abanico"]
    patch_order = {20: 62, 21: 75, 22: 89, 23: 102}
    for value in findall_local(fan, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        if fixture_id in patch_order:
            pairs = _pairs_of(value)
            for offset in caps[fixture_id].offsets_for_role(roles.PAN):
                pairs[offset] = patch_order[fixture_id]
            _write_pairs(value, pairs)
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [(f.function, f.fields["pans"]) for f in findings] == [
        ("Beams Abanico", "62, 89, 102, 75")
    ]
    assert findings[0].fixtures == (
        "BEAM 230W 7R #1",
        "BEAM 230W 7R #3",
        "BEAM 230W 7R #4",
        "BEAM 230W 7R #2",
    )


def test_2026_09_27_a_figure_owes_no_movement_to_a_spare(library):
    """2026-09-27, Round 2 review of the en-sala DMX audit: the waves carried
    the six washes the stage plot hides, because a figure that left them out
    was reported as moving half the group. Those spares took the propagation
    offsets, and the two rigged MACs were a ninth of a loop apart instead of a
    third. A figure owes movement to rigged heads only - and still to all of
    them: take a MAC out of the wave and the rule must name it.
    """
    from qlctool.checks.rule_movement_figure_coverage import RULE_ID
    from qlctool.rigged_fixture_ids import rigged_fixture_ids

    workspace = _show("Vibra.qxw")
    rigged = rigged_fixture_ids(workspace.root)
    wave = _efx_under(_functions_by_id(workspace), _functions(workspace)["Ola Vertical Washes"])
    for efx in wave:
        for head in findall_local(efx, "Fixture"):
            if int(find_local(head, "ID").text) not in rigged:
                efx.remove(head)
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert findings == []

    for efx in wave:
        for head in findall_local(efx, "Fixture"):
            if find_local(head, "ID").text == "34":
                efx.remove(head)
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert findings
    assert all(f.fixtures == ("MAC WASH 1915Z #2",) for f in findings)


def test_2026_09_27_a_pick_with_the_washes_held_is_still_a_wrapper(library):
    """2026-09-27, Round 2 review: `Jugar · Beams Abanico` became a two-member
    Collection when ruling D7 put the washes-held scene beside the fan, and
    `wrapper_scenes` - one member only - stopped seeing it, so the pick rules
    skipped it without a word. A Collection of Scenes is a wrapper too.
    """
    from qlctool.checks.wrapper_scenes import wrapper_scenes

    workspace = _show("Vibra.qxw")
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    ids = {graph.name(i): i for i in graph.functions}
    pick = ids["Jugar · Beams Abanico"]
    assert len(graph.members[pick]) == 2
    assert set(wrapper_scenes(graph, pick)) == set(graph.members[pick])
