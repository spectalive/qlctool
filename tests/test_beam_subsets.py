"""2026-08-27: per-beam accents must survive generation into the console.

The old desk could put prism and the continuous half-colour effect on one beam
or a mirrored pair. Losing those scenes removes live choices even though the
all-beam prism still makes the generated workspace look superficially complete.
"""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.generate.beam_subsets import generate_beam_subsets
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"
SUBSET_NAMES = ("1", "2", "3", "4", "1 y 3", "2 y 4")


def _functions(root):
    return {
        function.attrib["Name"]: function
        for function in find_local(root, "Engine")
        if localname(function) == "Function" and function.attrib.get("Name")
    }


def _scene_values(scene):
    values = {}
    for fixture in findall_local(scene, "FixtureVal"):
        pairs = [int(value) for value in (fixture.text or "").split(",") if value]
        values[int(fixture.attrib["ID"])] = dict(zip(pairs[::2], pairs[1::2]))
    return values


@pytest.fixture(scope="module")
def generated():
    workspace = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    result = generate_beam_subsets(workspace, library)
    beams = sorted(
        (
            capability
            for capability in capabilities_of(workspace.root, library)
            if not capability.is_smoke and capability.has_role(roles.PRISM)
        ),
        key=lambda capability: capability.fixture.address,
    )
    return workspace, result, beams


def test_prism_subsets_follow_dmx_address_and_park_every_other_beam(generated):
    """2026-08-27: fixture IDs do not define the operator's beam numbers."""
    workspace, _, beams = generated
    functions = _functions(workspace.root)

    cases = (("Prisma - 1", {0}), ("Prisma - 1 y 3", {0, 2}))
    for scene_name, selected in cases:
        values = _scene_values(functions[scene_name])
        for index, beam in enumerate(beams):
            offset, positions = beam.wheel_for_role(roles.PRISM)
            inserted = next(
                position for position in positions if position.preset == "PrismEffectOn"
            )
            parked = next(position for position in positions if position.preset == "PrismEffectOff")
            expected = inserted.middle if index in selected else parked.middle
            assert values[beam.fixture.fixture_id] == {offset: expected}


def test_multicolor_uses_the_half_colour_channel_without_moving_the_wheel(
    generated,
):
    """2026-08-27: both Colour channels share a role, but only one is this effect."""
    workspace, _, beams = generated
    values = _scene_values(_functions(workspace.root)["MultiColor - 2 y 4"])

    for index, beam in enumerate(beams):
        wheel_offset, _ = beam.wheel_for_role(roles.COLOR_MACRO)
        half_colour_offsets = set(beam.offsets_for_role(roles.COLOR_MACRO)) - {wheel_offset}
        assert len(half_colour_offsets) == 1
        half_colour_offset = half_colour_offsets.pop()
        assert values[beam.fixture.fixture_id] == {
            half_colour_offset: 255 if index in {1, 3} else 0
        }
        assert wheel_offset not in values[beam.fixture.fixture_id]


def test_every_restored_subset_is_reachable_from_the_generated_console():
    """2026-08-27: a generated function without a button is still lost."""
    workspace = Workspace.load(SHOW)
    build_canonical_show(workspace, FixtureLibrary.load())
    functions = _functions(workspace.root)
    function_ids = {name: int(function.attrib["ID"]) for name, function in functions.items()}
    button_function_ids = {
        int(target.attrib["ID"])
        for button in iter_local(workspace.root, "Button")
        if (target := find_local(button, "Function")) is not None
    }

    restored_names = {
        *(f"Prisma - {name}" for name in SUBSET_NAMES),
        "MultiColor - Todas",
        "MultiColor - Off",
        *(f"MultiColor - {name}" for name in SUBSET_NAMES),
    }
    assert restored_names <= function_ids.keys()
    assert {function_ids[name] for name in restored_names} <= button_function_ids
