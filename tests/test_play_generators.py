"""Phase 2 generator coverage for the 2026-09-02 JUGAR play page."""

from itertools import pairwise
from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.color_wheel_match import color_wheel_pairs
from qlctool.fog_offsets import fog_offsets
from qlctool.generate.canonical_show import FLASH_STROBE_FAST, build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.palette import PALETTE, PRIMARY_COLORS
from qlctool.shutter_open import shutter_open_pairs
from qlctool.strobe_speed import strobe_speed_pairs
from qlctool.white_level import white_level
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


@pytest.fixture(scope="module")
def built():
    """2026-09-02: construct the graph without changing shipped workspaces."""
    workspace = Workspace.load(SHOW)
    show = build_canonical_show(workspace, FixtureLibrary.load(), with_layout=False)
    return show, workspace


def _functions(workspace):
    return {
        function.attrib["ID"]: function
        for function in findall_local(find_local(workspace.root, "Engine"), "Function")
    }


def _members(function, functions):
    return [functions[step.text] for step in findall_local(function, "Step")]


def _values(function):
    return {
        int(value.attrib["ID"]): dict(zip(*[iter(map(int, value.text.split(",")))] * 2))
        for value in findall_local(function, "FixtureVal")
        if value.text
    }


def _wrapper_sources(wrapper_ids, functions):
    return [_members(functions[str(wrapper_id)], functions)[0] for wrapper_id in wrapper_ids]


def test_blackout_owns_open_shutters_without_emitting_light_or_smoke(built):
    """Todo Negro keeps RGB at zero while owning mechanical shutters open,
    so a later colour pick is visible and no smoke pump can start.
    """
    show, workspace = built
    functions = _functions(workspace)
    blackout = _values(functions[str(show.master_ids["Todo Negro"])])
    capabilities = capabilities_of(workspace.root, FixtureLibrary.load())
    min_washes = [
        capability for capability in capabilities if capability.fixture.model == "MiN Wash"
    ]

    assert len(min_washes) == 2
    for capability in min_washes:
        fixture_values = blackout[capability.fixture.fixture_id]
        colour_offsets = [
            offset
            for role in (roles.RED, roles.GREEN, roles.BLUE, roles.WHITE)
            for offset in capability.offsets_for_role(role)
        ]
        assert colour_offsets
        assert all(fixture_values[offset] == 0 for offset in colour_offsets)
        for offset, opening in shutter_open_pairs(capability):
            assert fixture_values[offset] == opening

    for capability in capabilities:
        if not capability.is_smoke:
            continue
        fixture_values = blackout.get(capability.fixture.fixture_id, {})
        assert all(fixture_values.get(offset) == 0 for offset in fog_offsets(capability))


def test_energy_levels_and_moments_use_the_combined_slow_owner(built):
    """2026-09-02: collections keep both optics moving through every state."""
    show, workspace = built
    functions = _functions(workspace)
    names = {function.attrib["Name"]: function for function in functions.values()}

    slow = names["Movimientos Suaves"]
    assert slow.attrib["Type"] == "Collection"
    assert {member.attrib["Name"] for member in _members(slow, functions)} == {
        "Suaves Washes",
        "Suaves Beams",
    }

    def state_members(name):
        return {member.attrib["Name"] for member in _members(names[name], functions)}

    assert "Movimientos Suaves" in state_members("Nivel Ambiente")
    assert "Movimientos Suaves" in state_members("Momento Tranquilo")
    assert "Movimientos Cabezas" in state_members("Nivel Fiesta")
    assert "Movimientos Cabezas" in state_members("Nivel Fiesta Dinamico")
    assert "Movimientos Rapidos" in state_members("Nivel Peak")


def test_rest_scenes_park_every_quiet_energy_level_and_moment(built):
    """2026-09-02: quiet states own focus, gobo and prism LTP channels."""
    _, workspace = built
    functions = _functions(workspace)
    names = {function.attrib["Name"]: function for function in functions.values()}

    assert _values(names["Gobo Reposo"]) == _values(names["Gobo - White Light"])
    assert _values(names["Prisma Reposo"]) == _values(names["Prisma - None"])

    for state_name in ("Nivel Ambiente", "Momento Charla", "Momento Tranquilo"):
        members = {member.attrib["Name"] for member in _members(names[state_name], functions)}
        assert {"Gobo Reposo", "Prisma Reposo"} <= members

    caps = capabilities_of(workspace.root, FixtureLibrary.load())
    focus_offsets = {
        capability.fixture.fixture_id: capability.offsets_for_role(roles.FOCUS)
        for capability in caps
        if capability.has_role(roles.GOBO)
    }
    values = _values(names["Gobo Reposo"])
    for fixture_id, offsets in focus_offsets.items():
        assert all(offset in values[fixture_id] for offset in offsets)

    for function in functions.values():
        if function.attrib["Type"] != "Scene" or not function.attrib["Name"].startswith("Gobo "):
            continue
        scene_values = _values(function)
        for fixture_id, offsets in focus_offsets.items():
            assert all(offset in scene_values[fixture_id] for offset in offsets)


def test_play_wrappers_are_single_member_collections_in_their_families(built):
    """2026-09-02: manual picks monitor wrappers, never state-owned leaves."""
    show, workspace = built
    functions = _functions(workspace)

    expected = {
        "Color": (show.play_wrappers.color_ids, 21),
        "Pixeles": (show.play_wrappers.panel_ids, 13),
        "Cabezas": (show.play_wrappers.movement_ids, 12),
        "Gobos": (show.play_wrappers.gobo_ids, 28),
        "Prisma": (show.play_wrappers.prism_ids, 9),
    }
    for family, (wrapper_ids, count) in expected.items():
        assert len(wrapper_ids) == count
        for wrapper_id in wrapper_ids:
            wrapper = functions[str(wrapper_id)]
            members = _members(wrapper, functions)
            assert wrapper.attrib["Type"] == "Collection"
            assert wrapper.attrib["Path"] == f"Jugar/{family}"
            assert len(members) == 1
            assert wrapper.attrib["Name"] == f"Jugar · {members[0].attrib['Name']}"

    assert len(show.play_wrappers.rainbow_ids) == 2
    assert all(
        functions[str(wrapper_id)].attrib["Path"] == "Jugar/Color"
        for wrapper_id in show.play_wrappers.rainbow_ids
    )

    names = {function.attrib["Name"]: function for function in functions.values()}
    color_wheel_sources = [step.text for step in findall_local(names["Rueda Colores"], "Step")]
    assert [
        source.attrib["ID"] for source in _wrapper_sources(show.play_wrappers.color_ids, functions)
    ] == color_wheel_sources
    assert [
        source.attrib["Name"]
        for source in _wrapper_sources(show.play_wrappers.rainbow_ids, functions)
    ] == [
        "Arcoiris Simultaneo",
        "Arcoiris Pasos",
    ]

    movement_sources = _wrapper_sources(show.play_wrappers.movement_ids, functions)
    assert [source.attrib["Name"] for source in movement_sources] == [
        "Movimiento Circulo",
        "Movimiento Ocho",
        "Movimiento Linea",
        "Movimiento Diamante",
        "Movimiento Cuadrado",
        "Movimiento Hoja",
        "Movimiento Lissajous",
        "Ola Vertical",
        "Barrido Unison",
        "Beams Abanico",
        "Beams Cruce",
        "Escenario",
    ]
    assert all(source.attrib["Type"] == "Collection" for source in movement_sources[:9])
    assert [source.attrib["Type"] for source in movement_sources[9:]] == ["Scene", "Scene", "Scene"]

    assert [
        source.attrib["Name"] for source in _wrapper_sources(show.play_wrappers.gobo_ids, functions)
    ] == [
        *(f"Gobo - Gobo {index}" for index in range(1, 18)),
        *(f"Gobo Repartido {index}" for index in range(1, 9)),
        "Gobo Shake - Gobo 1",
        "Gobo Shake - Gobo 9",
        "Gobo Shake - Gobo 17",
    ]
    assert [
        source.attrib["Name"]
        for source in _wrapper_sources(show.play_wrappers.prism_ids, functions)
    ] == [
        "Prisma - Insert Prism",
        "Prisma - 1",
        "Prisma - 2",
        "Prisma - 3",
        "Prisma - 4",
        "Prisma - 1 y 3",
        "Prisma - 2 y 4",
        "Prisma Giro Rapido",
        "Prisma Giro Inverso",
    ]

    panel_sources = [
        source.attrib["Name"]
        for source in _wrapper_sources(show.play_wrappers.panel_ids, functions)
    ]
    effect_numbers = [
        int(name.rsplit(" ", 1)[1])
        for name in panel_sources
        if name.startswith("Paneles - Effect ")
    ]
    assert effect_numbers[0] == 1
    assert effect_numbers[-1] == 42
    assert all(later - earlier <= 4 for earlier, later in pairwise(effect_numbers))
    assert panel_sources[-1] == "Paneles Manual"


def test_colour_hits_match_every_flash_100_fixture_and_strobe_write(built):
    """2026-09-02: every held palette hit has Flash 100%'s exact safe output
    footprint, including lit smoke fixtures and every pump shut at zero.
    """
    show, workspace = built
    functions = _functions(workspace)
    names = {function.attrib["Name"]: function for function in functions.values()}
    caps = capabilities_of(workspace.root, FixtureLibrary.load())
    flash_values = _values(names["Flash 100%"])
    expected_fixture_ids = set(flash_values)

    assert set(show.colour_flash_ids) == set(PRIMARY_COLORS)
    for color_name in PRIMARY_COLORS:
        hit = names[f"Golpe {color_name}"]
        hit_values = _values(hit)
        assert hit.attrib["Type"] == "Scene"
        assert hit.attrib["Path"] == "Golpes"
        assert set(hit_values) == expected_fixture_ids
        for capability in caps:
            fixture_id = capability.fixture.fixture_id
            if fixture_id not in hit_values:
                continue
            values = hit_values[fixture_id]
            flash = flash_values[fixture_id]
            for offset in capability.offsets_for_role(roles.STROBE):
                assert values.get(offset) == flash.get(offset)
            if capability.is_smoke:
                for offset in fog_offsets(capability):
                    assert values[offset] == 0
            for offset in capability.offsets_for_role(roles.WHITE):
                assert values[offset] == white_level(PALETTE[color_name])
            for offset, value in color_wheel_pairs(capability, color_name):
                assert values[offset] == value
            for offset in capability.offsets_for_role(roles.DIMMER):
                if offset not in dict(
                    strobe_speed_pairs(capability, FLASH_STROBE_FAST)
                ) and offset not in fog_offsets(capability):
                    assert values[offset] == 255
