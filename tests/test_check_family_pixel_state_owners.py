"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file continues the pixel-mode ownership region,
covering the graph-derived state owners (colour vs. pixel-mode) that a
renamed or wrapped family frame must not be able to hide.
"""

import copy

import pytest
from family_frame import family_frame as _family_frame
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from lxml import etree
from named_show import named_show as _show
from rig_root import RIG_ROOT
from twin_scene import twin_scene as _twin_scene

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.group_fixtures import group_fixtures
from qlctool.checks.lit import lit
from qlctool.checks.reach import reach
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.wheel_blade_offsets import wheel_blade_offsets
from qlctool.workspace import Workspace

REPO = RIG_ROOT


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


def test_a_multi_family_state_chaser_is_not_a_play_hook(library, deluxe_show):
    """2026-09-02: Ciclo Energia coordinates several families, so a family
    frame must not demand it as a return hook for each one.
    """
    from qlctool.capabilities_of import capabilities_of
    from qlctool.checks.build_show_graph import build_show_graph
    from qlctool.checks.group_fixtures import group_fixtures
    from qlctool.checks.room_states import room_states
    from qlctool.checks.state_owners import state_owners

    workspace = deluxe_show
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    states = room_states(workspace.root, graph, groups)
    owners = state_owners(graph, groups, states)
    energy_id = int(_functions(workspace)["Ciclo Energia"].attrib["ID"])

    assert not any(energy_id in function_ids for function_ids in owners.values())


def test_an_energy_nested_owner_missing_from_its_family_frame_is_reported(library):
    """2026-09-02: an owner within an energy-cycle level remains a required
    hook, while Ciclo Energia itself stays structural and unplayable.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show()
    functions = _functions(workspace)
    nested = _twin_scene(workspace, functions, "Gobo Reposo", "TEST energy gobo owner")
    level = functions["Nivel Ambiente"]
    etree.SubElement(level, f"{{{QLC_NS}}}Step").text = nested.attrib["ID"]
    _family_frame(workspace, ("Gobo Reposo",))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "TEST energy gobo owner" and "no tiene su Toggle" in f.message
        for f in findings
    ), "an energy-nested gobo owner went unnoticed"


def test_the_talk_owners_have_one_family_each(library, deluxe_show):
    """2026-09-02, re-review: colour and panel-mode recovery are separate
    state owners, so a renamed frame cannot hide shared hook semantics.
    """
    from qlctool.capabilities_of import capabilities_of
    from qlctool.checks.build_show_graph import build_show_graph
    from qlctool.checks.group_fixtures import group_fixtures
    from qlctool.checks.room_states import room_states
    from qlctool.checks.state_owners import state_owners

    workspace = deluxe_show
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    states = room_states(workspace.root, graph, groups)
    owners = state_owners(graph, groups, states)
    charla_id = int(_functions(workspace)["Luz Charla"].attrib["ID"])
    panels_id = int(_functions(workspace)["Paneles Charla"].attrib["ID"])

    assert charla_id in owners["color"]
    assert charla_id not in owners["pixel-mode"]
    assert panels_id not in owners["color"]
    assert panels_id in owners["pixel-mode"]


def test_color_hooks_do_not_take_the_panel_mode_contract(library, deluxe_show):
    """2026-09-02, re-review: graph-derived frame families keep COLOR from
    inheriting PIXELES ownership through a mode-resetting colour hook.
    """
    from qlctool.checks.function_families import function_families

    workspace = deluxe_show
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    for name in ("Rueda Colores", "Rueda Mezcla", "Luz Charla"):
        families = function_families(graph, groups, int(_functions(workspace)[name].attrib["ID"]))
        assert not families["pixel-mode"], name


def test_the_room_state_selector_is_not_a_family_handoff(library, deluxe_show):
    """2026-09-02, re-review: selecting a whole-room state is graph-distinct
    from replacing a family hook, even though both use a SoloFrame.
    """
    workspace = deluxe_show

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not findings


def test_a_scene_only_pixel_owner_requires_its_play_hook(library, deluxe_show):
    """2026-09-02, re-review: a direct Scene owner is still a state owner;
    only its write capability decides which JUGAR family must include it.
    """
    workspace = deluxe_show
    _family_frame(workspace, ("Ciclo Paneles Mixto",), caption="renamed")

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "Paneles Charla" and "no tiene su Toggle" in f.message for f in findings
    )


def test_a_renamed_frame_with_a_pixel_wrapper_requires_pixel_owners(library, deluxe_show):
    """2026-09-02, re-review: a wrapper's graph writes, not the frame
    caption, choose the family contract.
    """
    workspace = deluxe_show
    _family_frame(
        workspace,
        ("Rueda Colores", "Rueda Mezcla", "Luz Charla", "Jugar · Paneles - Effect 1"),
        caption="COLOR RENOMBRADO",
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    missing = {f.function for f in findings if "no tiene su Toggle" in f.message}
    assert {"Ciclo Paneles Mixto", "Paneles Charla"} <= missing


def test_a_complete_renamed_pixel_frame_is_silent(library, deluxe_show):
    """2026-09-02, re-review: the graph-derived pixel handoff does not need
    the colour wheel hooks, regardless of a frame's operator caption.
    """
    workspace = deluxe_show
    _family_frame(
        workspace,
        ("Ciclo Paneles Mixto", "Paneles Charla"),
        caption="no semantic label",
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not findings


def test_luz_charla_keeps_momento_intensity_outside_the_color_hook(library, deluxe_show):
    """2026-09-02: a COLOR pick stops Luz Charla but leaves Momento Charla's
    dimmer source running, while the hook still restores the beams' wheel.

    Ruling D8, 2026-09-27: the one dimmer a colour look does open is a
    wheel-only head's blade, which goes with its colour (`wheel_blade_offsets`).
    """
    workspace = deluxe_show
    functions = _functions(workspace)
    charla = functions["Luz Charla"]
    moment = functions["Momento Charla"]
    beam_white_id = functions["Color Beam - White"].attrib["ID"]
    charla_base_id = functions["Luz Charla Base"].attrib["ID"]
    charla_pixel_intensity_id = functions["Intensidad Charla Pixeles"].attrib["ID"]
    intensity_id = functions["Intensidad Total"].attrib["ID"]

    assert charla.attrib["Type"] == "Collection"
    members = {step.text for step in findall_local(charla, "Step")}
    assert members == {charla_base_id, beam_white_id}
    assert intensity_id not in members
    moment_members = {step.text for step in findall_local(moment, "Step")}
    assert intensity_id in moment_members
    assert charla_pixel_intensity_id in moment_members

    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    charla_writes = reach(
        graph,
        group_fixtures(workspace.root),
        int(charla.attrib["ID"]),
    )
    assert not any(
        graph.capabilities[fixture_id].roles_by_offset[offset] in (roles.DIMMER, roles.DIMMER_FINE)
        and lit(value)
        and offset not in wheel_blade_offsets(graph.capabilities[fixture_id])
        for fixture_id, offsets in charla_writes.items()
        for offset, value in offsets.items()
    )
    pick_writes = reach(
        graph,
        group_fixtures(workspace.root),
        int(functions["Rig Rojo + Pixeles"].attrib["ID"]),
    )
    assert not any(
        graph.capabilities[fixture_id].roles_by_offset[offset] in (roles.DIMMER, roles.DIMMER_FINE)
        and lit(value)
        and offset not in wheel_blade_offsets(graph.capabilities[fixture_id])
        for fixture_id, offsets in pick_writes.items()
        for offset, value in offsets.items()
    )
    moment_writes = reach(
        graph,
        group_fixtures(workspace.root),
        int(moment.attrib["ID"]),
    )
    colour_pick_fixtures = {
        fixture_id
        for fixture_id, offsets in pick_writes.items()
        if any(
            graph.capabilities[fixture_id].roles_by_offset[offset]
            in {
                roles.RED,
                roles.GREEN,
                roles.BLUE,
            }
            for offset in offsets
        )
    }
    missing_moment_intensity = {
        fixture_id
        for fixture_id in colour_pick_fixtures
        if graph.capabilities[fixture_id].offsets_for_role(roles.DIMMER)
        and not any(
            lit(moment_writes.get(fixture_id, {}).get(offset, 0))
            for offset in graph.capabilities[fixture_id].offsets_for_role(roles.DIMMER)
        )
    }
    assert not missing_moment_intensity, (
        "a COLOR pick can still paint fixtures whose moment owns no direct intensity: "
        f"{sorted(missing_moment_intensity)}"
    )
