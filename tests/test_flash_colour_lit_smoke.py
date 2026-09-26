"""2026-09-26, owner decision: the colour flash lights the lit smoke machines white.

Asked whether `Flash Color` and its desk burst should light the four vertical
LED fog machines (Vibra's fixtures 29-32), the owner answered: "Si, el flash
enciende las maquinas de humo en blanco". `Flash 100%` always wrote them white;
`Flash Color` skipped every smoke fixture, so while it was held the columns
kept the colour beneath, unstrobed, and read as dark beside the flash.

`rule_flash_lit_smoke` sees the cause; the bug is put back into today's Vibra
by taking the lit smoke machines out of `Flash Color` again.
"""

from pathlib import Path

import pytest
from rig_root import RIG_ROOT

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.flash_lights import flash_lights
from qlctool.checks.rule_flash_lit_smoke import RULE_ID
from qlctool.checks.strobe_written import strobe_capable_offsets, value_strobes
from qlctool.fog_offsets import fog_offsets
from qlctool.library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.workspace import Workspace
from qlctool.xmlutil import findall_local, iter_local

SETUPS = RIG_ROOT / "QLC+ Setups"
VIBRA = SETUPS / "Vibra.qxw"
CLUB = Path(__file__).resolve().parents[1] / "examples" / "small-club"
NAMES = default_names()


def _scene(workspace: Workspace, identifier: str):
    name = NAMES.display(identifier)
    return next(
        f
        for f in iter_local(workspace.root, "Function")
        if f.get("Type") == "Scene" and f.get("Name") == name
    )


def _values(scene) -> dict[int, dict[int, int]]:
    values: dict[int, dict[int, int]] = {}
    for fixture in findall_local(scene, "FixtureVal"):
        numbers = [int(n) for n in (fixture.text or "").split(",") if n]
        values[int(fixture.get("ID", "-1"))] = dict(zip(numbers[::2], numbers[1::2], strict=True))
    return values


@pytest.fixture(scope="module")
def vibra():
    workspace = Workspace.load(VIBRA)
    library = FixtureLibrary.load()
    return workspace, library, capabilities_of(workspace.root, library)


def test_2026_09_26_the_rule_bites_flash_color_without_the_columns(vibra):
    workspace, library, caps = vibra
    lit_smoke = {str(c.fixture.fixture_id) for c in caps if c.is_lit_smoke}
    assert lit_smoke
    for fixture in findall_local(_scene(workspace, "flash_colour"), "FixtureVal"):
        if fixture.get("ID") in lit_smoke:
            fixture.getparent().remove(fixture)
    found = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [f.function for f in found] == [NAMES.display("flash_colour")]
    assert len(found[0].fixtures) == len(lit_smoke)


def test_2026_09_26_flash_color_lights_the_columns_white_and_leaves_the_pump(vibra):
    _, _, caps = vibra
    workspace = Workspace.load(VIBRA)
    colour = _values(_scene(workspace, "flash_colour"))
    full = _values(_scene(workspace, "flash_full"))
    columns = [c for c in caps if c.is_lit_smoke]
    assert sorted(c.fixture.fixture_id for c in columns) == [29, 30, 31, 32]
    for capability in columns:
        written = colour[capability.fixture.fixture_id]
        pump = set(fog_offsets(capability))
        assert pump and not pump & set(written)
        for role in (roles.DIMMER, roles.RED, roles.GREEN, roles.BLUE):
            assert all(written[o] == 255 for o in capability.offsets_for_role(role))
        # The owner's constraint on its own: the columns go white, not strobing.
        strobes = strobe_capable_offsets(capability)
        assert strobes
        assert not any(
            o in written and value_strobes(strobing, written[o]) for o, strobing in strobes.items()
        )
        # Exactly Flash 100%'s white, minus the pump that scene shuts.
        expected = {o: v for o, v in full[capability.fixture.fixture_id].items() if o not in pump}
        assert written == expected
    fog_only = [c for c in caps if c.is_smoke and not c.is_lit_smoke]
    assert fog_only and all(c.fixture.fixture_id not in colour for c in fog_only)


@pytest.mark.parametrize(
    ("path", "fixtures"),
    [
        (SETUPS / "Vibra.qxw", None),
        (SETUPS / "Vibra-beats.qxw", None),
        (SETUPS / "Vibra-split.qxw", None),
        (CLUB / "club.qxw", CLUB / "fixtures"),
    ],
    ids=lambda p: p.name if isinstance(p, Path) else "",
)
def test_2026_09_26_the_rule_is_silent_on_every_shipped_workspace(path, fixtures):
    library = FixtureLibrary.load(None if fixtures is None else [fixtures])
    found = check_workspace(Workspace.load(path), library)
    assert [f for f in found if f.rule_id == RULE_ID] == []


class _DimmerlessColumn:
    """A lit smoke machine whose LEDs have red, green and blue and no dimmer."""

    is_lit_smoke = True
    is_smoke = True

    def offsets_for_role(self, role: str) -> list[int]:
        return {roles.RED: [1], roles.GREEN: [2], roles.BLUE: [3]}.get(role, [])


def test_2026_09_26_a_column_is_lit_by_its_colour_not_by_its_dimmer_alone(vibra):
    _, _, caps = vibra
    column = next(c for c in caps if c.is_lit_smoke)
    dimmer = column.offsets_for_role(roles.DIMMER)[0]
    rgb = [column.offsets_for_role(r)[0] for r in (roles.RED, roles.GREEN, roles.BLUE)]
    assert not flash_lights(column, {dimmer: 255, **dict.fromkeys(rgb, 0)})
    assert flash_lights(column, {dimmer: 255, **dict.fromkeys(rgb, 255)})
    assert not flash_lights(column, dict.fromkeys(rgb, 255))
    dimmerless = _DimmerlessColumn()
    assert flash_lights(dimmerless, {1: 255, 2: 255, 3: 255})  # type: ignore[arg-type]
    assert not flash_lights(dimmerless, {1: 0, 2: 0, 3: 0})  # type: ignore[arg-type]
