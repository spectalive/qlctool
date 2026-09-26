"""2026-09-25, owner requirement: a smoke machine with its own light is a wash, smoke or not.

Taking the vertical-smoke light chaser away from a rig without columns must
not take the columns' light away from a rig with them: the LED half of a lit
smoke machine joins the room's colour like a floor PAR (`color_scene.py`) and
its LED master rides the energy levels at full, while every scene that owns
the room holds its pump at zero (`fog_off.py`). Pinned on the frozen Vibra and
on Vibra with its fog-only machine (fixture 17) removed.
"""

import pytest
from rig_root import RIG_ROOT

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.capability import FixtureCapabilities
from qlctool.cli import main
from qlctool.fog_offsets import fog_offsets
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.internal_program import internal_program
from qlctool.library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.workspace import Workspace
from qlctool.xmlutil import findall_local, iter_local

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
RGB = (roles.RED, roles.GREEN, roles.BLUE)
Values = dict[int, dict[int, int]]
# The energy levels, the only scenes that own the room's brightness: each one
# holds every lit smoke machine's LED master at full (2026-09-25 review: one
# level at full was enough for the test to pass).
LEVELS = ("ambient_intensity", "full_intensity", "peak_intensity")


def _scenes(workspace: Workspace) -> dict[str, list[Values]]:
    """Every scene's values, fixture id -> {channel offset: value}, by scene name."""
    scenes: dict[str, list[Values]] = {}
    for function in iter_local(workspace.root, "Function"):
        if function.get("Type") != "Scene":
            continue
        values: Values = {}
        for fixture in findall_local(function, "FixtureVal"):
            numbers = [int(n) for n in (fixture.text or "").split(",") if n]
            values[int(fixture.get("ID", "-1"))] = dict(
                zip(numbers[::2], numbers[1::2], strict=True)
            )
        scenes.setdefault(function.get("Name", ""), []).append(values)
    return scenes


def _writes(caps: FixtureCapabilities, scene: Values, wanted: tuple[str, ...]) -> bool:
    channels = scene.get(caps.fixture.fixture_id, {})
    return all(o in channels for role in wanted for o in caps.offsets_for_role(role))


def _single_cell_washes(caps: list[FixtureCapabilities]) -> list[FixtureCapabilities]:
    """The rig's one-cell RGB fixtures that obey DMX colour: what a room colour paints."""
    return [
        c
        for c in caps
        if not c.is_smoke
        and len(c.offsets_for_role(roles.RED)) == 1
        and internal_program(c) is None
    ]


@pytest.fixture(scope="module", params=["vibra", "without-fog-only"])
def built(
    request, tmp_path_factory
) -> tuple[list[FixtureCapabilities], list[Values], dict[str, list[Values]]]:
    source = VIBRA
    if request.param == "without-fog-only":
        source = tmp_path_factory.mktemp("no17") / "no17.qxw"
        assert main(["patch", str(VIBRA), "--remove", "17", "--out", str(source)]) == 0
    workspace = Workspace.load(source)
    library = FixtureLibrary.load()
    build_canonical_show(workspace, library)
    named = _scenes(workspace)
    scenes = [values for group in named.values() for values in group]
    return capabilities_of(workspace.root, library), scenes, named


def test_2026_09_25_every_room_colour_paints_the_lit_smoke_machines(built):
    caps, scenes, _ = built
    lit = [c for c in caps if c.is_lit_smoke]
    assert lit, "Vibra's four vertical columns carry their own light"
    washes = _single_cell_washes(caps)
    room = [s for s in scenes if all(_writes(w, s, RGB) for w in washes)]
    assert room, "no scene paints the whole room"
    for scene in room:
        for machine in lit:
            assert _writes(machine, scene, RGB), machine.fixture.name
            pump = scene[machine.fixture.fixture_id]
            assert all(pump.get(o, 0) == 0 for o in fog_offsets(machine)), machine.fixture.name


def test_2026_09_25_the_levels_hold_the_lit_smoke_led_at_full_and_the_pump_at_zero(built):
    """Every energy level in LEVELS, not just one, holds each lit machine's LED
    master at full and its pump at zero, and states no colour: that is the room's."""
    caps, _, named = built
    names = default_names()
    lit = [c for c in caps if c.is_lit_smoke]
    assert lit
    for identifier in LEVELS:
        [level] = named[names.display(identifier)]
        for machine in lit:
            values = level.get(machine.fixture.fixture_id, {})
            where = f"{identifier}: {machine.fixture.name}"
            assert [values.get(o) for o in machine.offsets_for_role(roles.DIMMER)] == [255], where
            assert all(values.get(o) == 0 for o in fog_offsets(machine)), where
            assert not _writes(machine, level, RGB), where


def test_2026_09_25_no_scene_lights_a_smoke_machine_by_firing_it(built):
    """The light never needs the smoke: a scene painting the LED leaves the pump shut."""
    caps, scenes, _ = built
    for machine in (c for c in caps if c.is_lit_smoke):
        for scene in scenes:
            if _writes(machine, scene, RGB):
                pump = scene[machine.fixture.fixture_id]
                assert all(pump.get(o, 0) == 0 for o in fog_offsets(machine))
