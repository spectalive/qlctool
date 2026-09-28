"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers pixel-mode ownership inside the JUGAR
family frames - wrapped picks, nested frames, and the panels' own mode owner.
"""

import copy

import pytest
from family_frame import family_frame as _family_frame
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from lxml import etree
from named_show import named_show as _show
from rig_root import RIG_ROOT
from twin_scene import twin_scene as _twin_scene
from wrapper_button import wrapper_button as _wrapper_button

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.group_fixtures import group_fixtures
from qlctool.checks.reach import reach
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
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


def test_a_complete_family_frame_with_wrapped_picks_is_silent(library, deluxe_show):
    """2026-09-02, play-page design: complete hooks and an isolated wrapper
    let a pick replace AUTO without a state-driven start releasing it.
    """
    workspace = deluxe_show
    frame = _family_frame(
        workspace,
        (
            "Rueda Colores",
            "Rueda Mezcla",
            "Luz Charla",
            "Ciclo Paneles Mixto",
            "Paneles Charla",
        ),
    )
    _wrapper_button(workspace, frame, "Rig Rojo + Pixeles", "TEST wrapped red pick")

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not findings, "a correctly owned family frame should be silent"


def test_a_nested_family_frame_still_requires_every_state_owner(library):
    """2026-09-02, play-page design: a nested multipage frame still belongs
    to its nearest SoloFrame, so the missing Charla hook cannot hide inside it.
    """
    workspace = _show()
    _family_frame(workspace, ("Rueda Colores", "Rueda Mezcla"), nested=True)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(f.function == "Luz Charla" for f in findings)


def test_a_nested_family_frame_exempts_its_wrapper_pick(library, deluxe_show):
    """2026-09-02, play-page design: an inner plain/multipage frame inherits
    the complete outer SoloFrame and therefore keeps its wrapper layer exempt.
    """
    workspace = deluxe_show
    frame = _family_frame(
        workspace,
        (
            "Rueda Colores",
            "Rueda Mezcla",
            "Luz Charla",
            "Ciclo Paneles Mixto",
            "Paneles Charla",
        ),
        nested=True,
    )
    _wrapper_button(workspace, frame, "Rig Rojo + Pixeles", "TEST nested red pick")

    findings = check_workspace(workspace, library)
    assert not [f for f in findings if f.rule == "familia con dueño"]
    assert not [
        f
        for f in findings
        if f.rule == "capa que se suma al estado" and f.function == "TEST nested red pick"
    ]


def test_a_zero_panel_effect_is_still_pixel_mode_ownership(library, deluxe_show):
    """2026-09-02: mode zero is an intentional write, not an unowned channel."""
    from qlctool.checks.function_families import function_families

    workspace = deluxe_show
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    families = function_families(
        graph,
        group_fixtures(workspace.root),
        int(_functions(workspace)["Paneles Charla"].attrib["ID"]),
    )

    assert families["pixel-mode"]


def test_talk_panel_mode_and_pixel_base_keep_distinct_owners(library):
    """2026-09-02, re-review: programmed panels need a direct mode-only
    talk owner while Pixeles ON retains mode parking for other matrix fixtures.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra.qxw")
    build_canonical_show(workspace, library)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    functions = _functions(workspace)
    talk_panel_writes = reach(graph, groups, int(functions["Paneles Charla"].attrib["ID"]))
    pixel_base_writes = reach(graph, groups, int(functions["Pixeles ON"].attrib["ID"]))

    assert talk_panel_writes
    for fixture_id, writes in talk_panel_writes.items():
        written_roles = {
            graph.capabilities[fixture_id].roles_by_offset[offset] for offset in writes
        }
        assert written_roles == {roles.EFFECT}
        assert not any(
            graph.capabilities[fixture_id].roles_by_offset[offset] == roles.EFFECT
            for offset in pixel_base_writes.get(fixture_id, {})
        )

    assert any(
        roles.EFFECT
        in {graph.capabilities[fixture_id].roles_by_offset[offset] for offset in writes}
        for fixture_id, writes in pixel_base_writes.items()
        if fixture_id not in talk_panel_writes
    ), "Pixeles ON stopped parking every non-cycle matrix fixture mode"


def test_a_moments_pixel_intensity_companion_is_not_a_second_play_hook(library, deluxe_show):
    """2026-09-02: a moment's panel intensity support must not take over
    pixel mode or demand a duplicate PIXELES hook.
    """
    workspace = deluxe_show

    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    writes = reach(
        graph,
        group_fixtures(workspace.root),
        int(_functions(workspace)["Intensidad Charla Pixeles"].attrib["ID"]),
    )
    assert not any(
        graph.capabilities[fixture_id].roles_by_offset[offset] == roles.EFFECT
        for fixture_id, offsets in writes.items()
        for offset in offsets
    )
    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not any(f.function == "Intensidad Charla Pixeles" for f in findings)


def test_a_bare_pixel_mode_state_owner_still_requires_its_play_hook(library, deluxe_show):
    """2026-09-02: adding a second functional pixel owner to AUTO requires
    its own PIXELES hook; an intensity-only companion must not hide it.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = deluxe_show
    functions = _functions(workspace)
    copied = _twin_scene(
        workspace,
        functions,
        "Ciclo Paneles Mixto",
        "TEST independent pixel owner",
    )
    etree.SubElement(functions["AUTO"], f"{{{QLC_NS}}}Step").text = copied.attrib["ID"]
    _family_frame(
        workspace,
        ("Rueda Colores", "Rueda Mezcla", "Luz Charla", "Ciclo Paneles Mixto"),
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "TEST independent pixel owner" and "no tiene su Toggle" in f.message
        for f in findings
    )


def test_a_nonmoving_rgb_effect_fixture_is_a_pixel_mode_owner(library, deluxe_show):
    """2026-09-02: pixel-mode ownership follows capabilities, even if a
    fixture type omits the word "pixel".
    """
    from dataclasses import replace
    from types import SimpleNamespace

    from qlctool.checks.is_pixel_fixture import is_pixel_fixture as _is_pixel_fixture

    workspace = deluxe_show
    capability = next(
        c for c in capabilities_of(workspace.root, library) if c.fixture.fixture_id == 24
    )

    assert _is_pixel_fixture(replace(capability, fixture_type="LED PAR"))
    assert not _is_pixel_fixture(
        SimpleNamespace(is_smoke=False, roles=frozenset(capability.roles - {roles.EFFECT}))
    )
    assert not _is_pixel_fixture(
        SimpleNamespace(is_smoke=False, roles=frozenset({*capability.roles, roles.PAN}))
    )


def test_a_state_started_movement_collection_is_its_own_required_hook(library, deluxe_show):
    """2026-09-02, play-page design: future `Movimientos Suaves` is a
    functional Collection started by a state. Its hook is required, but its
    two child movement functions are not separate hooks.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS
    from qlctool.functions.build_collection import build_collection
    from qlctool.next_function_id import next_function_id
    from qlctool.vc.build_button import build_button
    from qlctool.vc.next_widget_id import next_widget_id

    workspace = deluxe_show
    functions = _functions(workspace)
    washes_id = next_function_id(workspace.root)
    workspace.add_function(
        build_collection(
            washes_id, "TEST Suaves Washes", [int(functions["Suaves Washes"].attrib["ID"])]
        )
    )
    beams_id = next_function_id(workspace.root)
    workspace.add_function(
        build_collection(
            beams_id,
            "TEST Suaves Beams",
            [int(functions["Suaves Beams"].attrib["ID"])],
        )
    )
    smooth_id = next_function_id(workspace.root)
    workspace.add_function(
        build_collection(smooth_id, "TEST Movimientos Suaves", [washes_id, beams_id])
    )
    etree.SubElement(functions["AUTO"], f"{{{QLC_NS}}}Step").text = str(smooth_id)

    frame = _family_frame(workspace, ("Movimientos Suaves",))
    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(f.function == "TEST Movimientos Suaves" for f in findings)

    build_button(
        frame,
        next_widget_id(workspace.root),
        "TEST Movimientos Suaves",
        smooth_id,
        x=220,
        y=30,
        width=105,
        height=50,
    )
    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not [f for f in findings if f.function in {"TEST Suaves Washes", "TEST Suaves Beams"}]
