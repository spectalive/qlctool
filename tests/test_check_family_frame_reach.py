"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers the JUGAR family frames' own-hook
requirement and the state/pick darkness check (`pick que apaga`).
"""

import copy

import pytest
from button_of import button_of as _button_of
from family_frame import family_frame as _family_frame
from fixture_val_pairs import fixture_val_pairs as _pairs_of
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from lxml import etree
from named_show import named_show as _show
from rig_root import RIG_ROOT
from wrapper_button import wrapper_button as _wrapper_button
from write_fixture_val_pairs import write_fixture_val_pairs as _write_pairs

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.group_fixtures import group_fixtures
from qlctool.checks.room_states import room_states
from qlctool.checks.rule_pick_darkens import check_pick_darkens
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOWS = ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw")


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


@pytest.fixture(scope="module")
def _deluxe_built(library):
    """The DeluxeEventos2 rig through the canonical generator, built once."""
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    return workspace.root


@pytest.fixture
def deluxe_show(_deluxe_built):
    """A private copy of that build, so a test that edits it changes no other."""
    return Workspace(etree.ElementTree(copy.deepcopy(_deluxe_built)))


def test_a_family_pick_that_is_reachable_from_a_room_state(library):
    """2026-09-02, play-page design: a wheel step used as its own pick
    reports that state-driven start to the SoloFrame and releases the hook.
    The pick must target a one-member wrapper instead.
    """
    workspace = _show()
    _family_frame(
        workspace,
        ("Rueda Colores", "Rueda Mezcla", "Luz Charla", "Rig Rojo + Pixeles"),
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "Rig Rojo + Pixeles" and "es un pick" in f.message for f in findings
    ), "a state-reachable family pick went unnoticed"


def test_a_family_frame_missing_a_state_owner(library):
    """2026-09-02, play-page design: Momento Charla colours the rig through
    Luz Charla, so the COLOR frame needs that hook as well as the AUTO wheel.
    """
    workspace = _show()
    _family_frame(workspace, ("Rueda Colores", "Rueda Mezcla"))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "Luz Charla" and "no tiene su Toggle" in f.message for f in findings
    ), "a family frame missing Luz Charla's hook went unnoticed"


def test_a_pick_cannot_dark_a_moment_by_stopping_its_hook(library, deluxe_show):
    """2026-09-02: pressing a COLOR pick stops its hook. If that hook alone
    opens Momento Charla's dimmers, the pick paints a black room.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = deluxe_show
    functions = _functions(workspace)
    charla = functions["Luz Charla"]
    moment = functions["Momento Charla"]
    intensity_id = functions["Intensidad Total"].attrib["ID"]

    for step in findall_local(moment, "Step"):
        if step.text == intensity_id:
            moment.remove(step)
    if intensity_id not in {step.text for step in findall_local(charla, "Step")}:
        etree.SubElement(charla, f"{{{QLC_NS}}}Step").text = intensity_id

    findings = [f for f in check_workspace(workspace, library) if f.rule == "pick que apaga"]
    assert any(f.function == "Momento Charla" for f in findings), (
        "a pick darkening Momento Charla by stopping Luz Charla went unnoticed"
    )


def test_a_pick_only_colour_cannot_leave_a_dimmer_unwritten(library):
    """2026-09-02: a latched JUGAR pick can be the only colour after it stops
    Momento Charla's hook, so it still needs a dimmer writer.
    """
    workspace = _show("Vibra.qxw")
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    panel = next(
        capability
        for capability in graph.capabilities.values()
        if "WX-60WPS" in capability.fixture.name
    )
    functions = _functions(workspace)
    moment = functions["Momento Charla"]
    charla_id = functions["Luz Charla"].attrib["ID"]
    for step in findall_local(moment, "Step"):
        if step.text != charla_id:
            moment.remove(step)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "pick que apaga"]

    assert any(
        f.function == "Momento Charla" and panel.fixture.name in f.fixtures for f in findings
    ), "a pick-only colour with no dimmer writer went unnoticed"


def test_pick_darkens_checks_a_state_with_no_active_hook(library):
    """2026-09-02: Todo Negro reaches none of the COLOR frame's hooks, but a
    latched colour pick still runs beside it and needs an open shutter owner.
    """
    workspace = _show("Vibra-split.qxw")
    capabilities = capabilities_of(workspace.root, library)
    graph = build_show_graph(workspace.root, capabilities)
    groups = group_fixtures(workspace.root)
    functions = _functions(workspace)
    black_id = int(functions["Todo Negro"].attrib["ID"])
    charla_id = int(functions["Momento Charla"].attrib["ID"])
    pick_name = "Jugar · Rig Rojo + Pixeles"

    hook_ids = {int(functions[name].attrib["ID"]) for name in ("Rueda Colores", "Luz Charla")}
    assert not hook_ids & graph.descendants(black_id)

    min_washes = {
        capability.fixture.fixture_id: capability
        for capability in capabilities
        if capability.fixture.model == "MiN Wash"
    }
    assert len(min_washes) == 2
    for value in findall_local(functions["Todo Negro"], "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        capability = min_washes.get(fixture_id)
        if capability is None:
            continue
        pairs = _pairs_of(value)
        for shutter in capability.offsets_for_role(roles.STROBE):
            pairs.pop(shutter, None)
        _write_pairs(value, pairs)

    graph = build_show_graph(workspace.root, capabilities)
    findings = check_pick_darkens(
        graph,
        groups,
        workspace.root,
        {black_id, charla_id},
    )

    assert any(
        finding.function == "Todo Negro"
        and f"«{pick_name}»" in finding.message
        and set(finding.fixtures) == {"MiN Wash #1", "MiN Wash #2"}
        for finding in findings
    ), "the no-active-hook state/pick pair was skipped"


def test_pick_darkens_reuses_instant_root_states(library):
    """One room state is evaluated beside every latched pick; its immutable
    graph states must not be rebuilt once per fixture channel and pick.

    The ceiling is an order of magnitude, not a budget: without the cache one
    state cost millions of node visits. It moves when the show gains picks,
    because every pick is another `stopped` frontier and therefore another key -
    48,000 since 2026-09-22, when the colour wheel split into three modes and
    every movement figure gained its two twins (41,663 measured).
    """
    import cProfile

    workspace = _show("Vibra-split.qxw")
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    charla_id = int(_functions(workspace)["Momento Charla"].attrib["ID"])
    profiler = cProfile.Profile()

    profiler.runcall(
        check_pick_darkens,
        graph,
        groups,
        workspace.root,
        {charla_id},
    )

    node_state_calls = sum(
        entry.callcount
        for entry in profiler.getstats()
        if getattr(entry.code, "co_name", "") == "_node_states"
    )
    assert node_state_calls < 48_000, (
        f"one state rebuilt {node_state_calls} instant graph nodes across its picks"
    )


@pytest.mark.parametrize("name", SHOWS)
def test_every_regenerated_show_has_no_dark_state_pick_pair(name, library):
    """The generator fixes the state/pick behavior without touching shipped
    workspaces in this focused fix wave.
    """
    workspace = _show(name)
    build_canonical_show(workspace, library, with_layout=False)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    states = room_states(workspace.root, graph, groups)

    findings = check_pick_darkens(graph, groups, workspace.root, states)

    assert not findings, "\n".join(str(finding) for finding in findings)


def test_a_higher_pick_shutter_value_can_close_a_concurrent_state(library):
    """2026-09-02: HTP chooses the higher shutter value, not whichever
    concurrent root the predicate happened to visit first.
    """
    from lxml import etree

    from qlctool.capability import Capability
    from qlctool.constants import QLC_NS
    from qlctool.functions.build_scene import build_scene
    from qlctool.next_function_id import next_function_id

    workspace = _show("Vibra.qxw")
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    functions = _functions(workspace)
    mac = graph.capabilities[33]
    shutter = mac.offsets_for_role(roles.STROBE)[0]
    mac.capabilities_by_offset[shutter] = (
        Capability(0, 9, "Open", "ShutterOpen"),
        Capability(10, 255, "Closed", "ShutterClose"),
    )
    open_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(open_id, "TEST low shutter", {33: [(shutter, 0)]}))
    etree.SubElement(functions["Momento Charla"], f"{{{QLC_NS}}}Step").text = str(open_id)
    closed_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(closed_id, "TEST high shutter pick", {33: [(shutter, 255), (8, 255)]})
    )
    _family_frame(workspace, ("Luz Charla", "TEST high shutter pick"))
    graph = build_show_graph(workspace.root, list(graph.capabilities.values()))
    states = room_states(workspace.root, graph, groups)

    findings = check_pick_darkens(graph, groups, workspace.root, states)

    assert any(
        f.function == "Momento Charla" and mac.fixture.name in f.fixtures for f in findings
    ), "a higher closed shutter value did not win its concurrent open value"


def test_pick_darkens_checks_each_pick_and_ignores_flash_buttons(library):
    """2026-09-02: every Toggle pick is checked independently, while a Flash
    does not latch and must not be treated as a SoloFrame replacement.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show("Vibra.qxw")
    functions = _functions(workspace)
    charla_id = functions["Luz Charla"].attrib["ID"]
    for state_name in ("Momento Charla", "Momento Tranquilo"):
        state = functions[state_name]
        for step in findall_local(state, "Step"):
            state.remove(step)
        step = etree.SubElement(state, f"{{{QLC_NS}}}Step")
        step.text = charla_id
    first_pick = "Jugar · Rig Rojo + Pixeles"
    second_pick = "Jugar · Rig Verde + Pixeles"
    first_button = _button_of(workspace, functions[first_pick].attrib["ID"])
    action = find_local(first_button, "Action")
    action.text = "Flash"
    action.attrib.clear()

    findings = [f for f in check_workspace(workspace, library) if f.rule == "pick que apaga"]

    assert not any(f"«{first_pick}»" in f.message for f in findings)
    assert {
        "Momento Charla",
        "Momento Tranquilo",
    } <= {finding.function for finding in findings if f"«{second_pick}»" in finding.message}


def test_a_family_hook_reachable_from_another_frame_button(library):
    """2026-09-02, play-page design: a wrapper over a hook in the same
    SoloFrame starts that hook and immediately makes the frame stop it.
    """
    workspace = _show()
    frame = _family_frame(workspace, ("Rueda Colores", "Rueda Mezcla", "Luz Charla"))
    _wrapper_button(workspace, frame, "Rueda Colores", "TEST wrapped colour hook")

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "TEST wrapped colour hook" and "arranca el hook" in f.message
        for f in findings
    ), "a family hook started by another frame button went unnoticed"
