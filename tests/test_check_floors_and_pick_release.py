"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers the 2026-09-26/27 en-sala DMX audit -
the vertical smoke columns' own strobe, a state's static floor exemption
(D8), a released pick leaving orphaned writes behind, and a turned EFX
figure sweeping tilt past the measured audience window.
"""

import pytest
from fixture_val_pairs import fixture_val_pairs as _pairs_of
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show
from twin_scene import twin_scene as _twin_scene
from write_fixture_val_pairs import write_fixture_val_pairs as _write_pairs

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.group_fixtures import group_fixtures
from qlctool.checks.room_states import room_states
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary

SHOWS = ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw")


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def _set_steps(collection, ids):
    """Rewrite a Collection's members, in order."""
    template = findall_local(collection, "Step")[0]
    for step in findall_local(collection, "Step"):
        collection.remove(step)
    for number, function_id in enumerate(ids):
        step = collection.makeelement(template.tag, {"Number": str(number)})
        step.text = str(function_id)
        collection.append(step)


def test_2026_09_26_the_columns_do_not_strobe_on_strobo(library):
    """2026-09-26, en-sala DMX audit (items 7 and 14): STROBO, STROBO SUAVE,
    FLASH and FLASH LENTO strobed every fixture but the four vertical smoke
    columns, whose LED has a strobe channel of its own ("Strobe, slow to
    fast"). Every strobe writer skipped the whole smoke machine, pump and
    LED alike, and both rules skipped it too. Ruling D3: the columns strobe
    with the rig and the pump is never written; `Flash Color`, which keeps
    the running colour, lights them white and steady (owner, 2026-09-26).
    Strip the columns out of STROBO, or park their strobe in FLASH, and the
    rules must name all four; `Flash Color` stays silent.
    """
    from qlctool.checks.rule_flash_strobe import check_flash_strobe
    from qlctool.checks.rule_strobe_coverage import check_strobe_coverage

    columns = ("Humo Vertical 1", "Humo Vertical 2", "Humo Vertical 3", "Humo Vertical 4")

    def findings(workspace):
        graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
        groups = group_fixtures(workspace.root)
        return check_strobe_coverage(graph, groups) + check_flash_strobe(
            graph, groups, workspace.root
        )

    for name in SHOWS:
        assert findings(_show(name)) == []

    workspace = _show()
    capabilities = {
        c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library) if c.is_lit_smoke
    }
    assert sorted(c.fixture.name for c in capabilities.values()) == list(columns)
    functions = _functions(workspace)
    for value in list(findall_local(functions["Strobo Rapido"], "FixtureVal")):
        if int(value.attrib["ID"]) in capabilities:
            value.getparent().remove(value)
    for value in findall_local(functions["Flash 100%"], "FixtureVal"):
        capability = capabilities.get(int(value.attrib["ID"]))
        if capability is None:
            continue
        pairs = _pairs_of(value)
        for offset in capability.offsets_for_role(roles.STROBE):
            pairs[offset] = 0
        _write_pairs(value, pairs)

    found = {(f.function, f.fixtures) for f in findings(workspace)}
    assert found == {("Strobo Rapido", columns), ("Flash 100%", columns)}


def test_2026_09_27_a_floor_under_the_gobo_hook_is_not_a_collision(library):
    """2026-09-27, en-sala fix round 3 (ruling D8): a released Gobo Shake kept
    shaking under FIESTA because nothing the state still ran wrote the gobo
    channels. A Scene started before the hook is overridden by the hook while
    it runs and writes again the tick a pick over it stops - measured on
    :9995, gobo and shake back on the Scene's values the tick the pick was
    released. Put first, it is a floor: no collision, and not an owner the
    frame lacks. Put after the hook, it is two looks fighting, and both rules
    must say so.
    """
    from qlctool.checks.static_floors import static_floors

    workspace = _show()
    functions = _functions(workspace)
    fiesta = functions["Momento Fiesta"]
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    floors = static_floors(
        graph, groups, int(fiesta.attrib["ID"]), room_states(workspace.root, graph, groups)
    )
    members = [int(s.text) for s in findall_local(fiesta, "Step") if int(s.text) not in floors]
    floor = int(_twin_scene(workspace, functions, "Gobo Reposo", "Gobo Suelo").attrib["ID"])

    _set_steps(fiesta, [floor, *members])
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    assert static_floors(
        graph, groups, int(fiesta.attrib["ID"]), room_states(workspace.root, graph, groups)
    ) == {floor}
    found = {(f.rule_id, f.function) for f in check_workspace(workspace, library)}
    assert ("collision", "Momento Fiesta") not in found
    assert ("family_owner", "Gobo Suelo") not in found

    _set_steps(fiesta, [*members, floor])
    found = {(f.rule_id, f.function) for f in check_workspace(workspace, library)}
    assert ("collision", "Momento Fiesta") in found
    assert ("family_owner", "Gobo Suelo") in found


def test_2026_09_27_a_floor_is_only_a_state_s_and_only_ltp(library):
    """2026-09-27, round 3 review (I-2, M-8): the floor exemption is the D8
    fallback under a room state's hooks, nothing more. The same LTP-only Scene
    put first in a pick's own Collection, under a member that writes the 7R
    wheel too, is a look nobody sees and still a collision. And a Scene that
    also writes an HTP channel is merged, not ordered: first in a state, it
    is no floor and collides.
    """
    from qlctool.checks.static_floors import static_floors

    workspace = _show()
    functions = _functions(workspace)
    wrapper = functions["Rig Rojo + Pixeles"]
    members = [int(s.text) for s in findall_local(wrapper, "Step")]
    wheel = int(_twin_scene(workspace, functions, "Color Beam - White", "Beam Suelo").attrib["ID"])
    _set_steps(wrapper, [wheel, *members])
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    states = room_states(workspace.root, graph, groups)
    assert int(wrapper.attrib["ID"]) not in states
    assert static_floors(graph, groups, int(wrapper.attrib["ID"]), states) == frozenset()
    found = {(f.rule_id, f.function) for f in check_workspace(workspace, library)}
    assert ("collision", "Rig Rojo + Pixeles") in found

    workspace = _show()
    functions = _functions(workspace)
    capabilities = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    fiesta = functions["Momento Fiesta"]
    graph = build_show_graph(workspace.root, list(capabilities.values()))
    states = room_states(workspace.root, graph, groups)
    floors = static_floors(graph, groups, int(fiesta.attrib["ID"]), states)
    members = [int(s.text) for s in findall_local(fiesta, "Step") if int(s.text) not in floors]
    lit_floor = _twin_scene(workspace, functions, "Gobo Reposo", "Gobo Suelo Encendido")
    for value in findall_local(lit_floor, "FixtureVal"):
        capability = capabilities[int(value.attrib["ID"])]
        pairs = _pairs_of(value)
        pairs.update(dict.fromkeys(capability.offsets_for_role(roles.DIMMER), 255))
        _write_pairs(value, pairs)
    _set_steps(fiesta, [int(lit_floor.attrib["ID"]), *members])
    graph = build_show_graph(workspace.root, list(capabilities.values()))
    assert static_floors(graph, groups, int(fiesta.attrib["ID"]), states) == frozenset()
    found = {(f.rule_id, f.function) for f in check_workspace(workspace, library)}
    assert ("collision", "Momento Fiesta") in found


def test_2026_09_26_releasing_a_pick_leaves_the_beams_red(library):
    """2026-09-26, en-sala DMX audit (item 5 and concern C3): with AUTO running,
    `Rig Rojo` on and off left every RGB fixture black and the four 7R lit and
    red - their wheel is LTP, their blade was held open by the level, and
    QLC+ 5 restarts no hook when a Toggle goes off. Gobo Shake kept shaking
    under FIESTA, and a released figure left the heads with nothing aiming
    them. Ruling D8: picks stay latched and the release is clean. Hold the
    blade open from the levels again, or take the states' floors away, and
    the rule must name the beams (and the MACs for a figure).
    """
    from qlctool.checks.finding import ERROR, WARNING
    from qlctool.checks.rule_pick_release_orphans import check_pick_release_orphans
    from qlctool.checks.static_floors import static_floors

    def findings(workspace):
        graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
        groups = group_fixtures(workspace.root)
        states = room_states(workspace.root, graph, groups)
        found = check_pick_release_orphans(graph, groups, workspace.root, states)
        return {f.function: f for f in found}, graph, groups, states

    for name in SHOWS:
        assert findings(_show(name))[0] == {}

    workspace = _show()
    capabilities = capabilities_of(workspace.root, library)
    beams = {c.fixture.fixture_id: c for c in capabilities if c.has_role(roles.GOBO)}
    names = tuple(sorted(c.fixture.name for c in beams.values()))
    functions = _functions(workspace)
    for level in ("Intensidad Ambiente", "Intensidad Total", "Intensidad Peak"):
        for value in findall_local(functions[level], "FixtureVal"):
            capability = beams.get(int(value.attrib["ID"]))
            if capability is not None:
                pairs = _pairs_of(value)
                pairs.update(dict.fromkeys(capability.offsets_for_role(roles.DIMMER), 255))
                _write_pairs(value, pairs)
    found = findings(workspace)[0]
    rojo = found["Jugar · Rig Rojo + Pixeles"]
    assert (rojo.severity, rojo.fixtures) == (ERROR, names)
    assert "AUTO" in rojo.fields["states"]

    workspace = _show()
    _, graph, groups, states = findings(workspace)
    by_id = {int(f.attrib["ID"]): f for f in _functions(workspace).values()}
    for state_id in states:
        floors = static_floors(graph, groups, state_id, states)
        if floors:
            kept = [m for m in graph.members[state_id] if m not in floors]
            _set_steps(by_id[state_id], kept)
    found = findings(workspace)[0]
    shake = found["Jugar · Gobo Shake - Gobo 1"]
    assert (shake.severity, shake.fixtures) == (WARNING, names)
    assert "Momento Fiesta" in shake.fields["states"]
    figure = found["Jugar · Movimiento Circulo"]
    assert figure.severity == WARNING
    assert figure.fixtures == (*names, "MAC WASH 1915Z #1", "MAC WASH 1915Z #2")
    # Audit item 16: the prism rotation stayed latched at 224 after Giro Inverso.
    spin = found["Jugar · Prisma Giro Inverso"]
    assert (spin.severity, spin.fixtures) == (WARNING, names)
    assert "Momento Fiesta" in spin.fields["states"]
    # The panels kept a released pick's programme under CHARLA (review I-1).
    panels = found["Jugar · Paneles - Effect 1"]
    assert panels.severity == WARNING
    assert all(name.startswith("WX-60WPS-48PARTITION") for name in panels.fixtures)
    assert "Momento Charla" in panels.fields["states"]


def test_2026_09_27_a_turned_figure_that_leaves_the_audience(library):
    """2026-09-27, the en-sala DMX re-audit (item 2): every Diamante put the
    7R at tilt 200-240 about 30% of the time, past the 207-234 window, and
    Hoja about 7%, while `movement_window` passed them. It judged `offset +-
    Height` on tilt, which is only the reach at Rotation 0: QLC+ scales and
    turns the figure in one step, so a Diamond of Width 20 and Height 13
    turned 90 degrees swings tilt by 20. Put that Diamond back on the beams
    and the rule must name the tilt it draws; the same figure unturned must
    pass; a Circle turned 45 degrees (`Cascada Beams`) must bite too.
    """

    def outside(algorithm, rotation):
        workspace = _show()
        efx = _functions(workspace)["Beam Circulo"]
        find_local(efx, "Algorithm").text = algorithm
        find_local(efx, "Width").text = "20"
        find_local(efx, "Height").text = "13"
        find_local(efx, "Rotation").text = str(rotation)
        for axis in findall_local(efx, "Axis"):
            find_local(axis, "Offset").text = "82" if axis.attrib["Name"] == "X" else "220"
        return [
            f.fields["outside"]
            for f in check_workspace(workspace, library)
            if f.rule_id == "movement_window" and f.function == "Beam Circulo"
        ]

    assert outside("Diamond", 90) == ["tilt 200..240"]
    assert outside("Diamond", 0) == []
    assert outside("Circle", 45) == ["tilt 203.1..236.9"]
