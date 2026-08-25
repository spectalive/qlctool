"""Strobes, of the two kinds this rig can actually do.

A fixture with a shutter strobes itself: one channel value and it keeps
flashing. Only the fixtures whose definition *labels* a strobe range get driven
here - a MiN Wash's shutter channel puts "Closed" at 1-7, so guessing a value on
an unlabelled channel is how a head goes dark in the middle of a set.

Everything else - the LED bars and PARs - has no shutter, so it strobes the way
the hand-built show does it: a chaser flipping the whole rig between full and
black. Two speeds, because one is a hard strobe and the other is a pulse.
"""

from dataclasses import dataclass

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..shutter_open import shutter_open_pairs
from ..workspace import Workspace

FAST_MS = 50
MEDIUM_MS = 250


@dataclass(frozen=True)
class GeneratedStrobes:
    on_id: int | None
    off_id: int | None
    fast_id: int
    medium_id: int


def generate_strobe_effects(
    workspace: Workspace,
    library: FixtureLibrary,
    full_id: int,
    black_id: int,
    path: str = "Strobos",
) -> GeneratedStrobes:
    """Shutter strobe scenes plus two flash chasers over full/black scenes."""
    shutter = _shutter_values(workspace, library)

    on_id = off_id = None
    if shutter:
        on_id = _scene(workspace, "Strobo ON", {f: v for f, (v, _) in shutter.items()}, path)
        off_id = _scene(workspace, "Strobo OFF", {f: v for f, (_, v) in shutter.items()}, path)

    fast_id = _flash_chaser(workspace, "Strobo Rapido", full_id, black_id, FAST_MS, path)
    medium_id = _flash_chaser(
        workspace, "Strobo Medio", full_id, black_id, MEDIUM_MS, path
    )
    return GeneratedStrobes(
        on_id=on_id, off_id=off_id, fast_id=fast_id, medium_id=medium_id
    )


def _shutter_values(workspace: Workspace, library: FixtureLibrary):
    """fixture id -> (values that strobe it, values that reopen it).

    Both come from the definition's own labelled ranges, never from a guess -
    the reopen value through `shutter_open_pairs`, so a strobe that stops and a
    scene that opens a shutter always agree on where "open" is.
    """
    result: dict[int, tuple[list[tuple[int, int]], list[tuple[int, int]]]] = {}
    for capability in capabilities_of(workspace.root, library):
        if capability.is_smoke:
            continue
        strobing: list[tuple[int, int]] = []
        opening: list[tuple[int, int]] = []
        # One source of truth for "what value opens this shutter": the range the
        # definition marks `ShutterOpen`, read by shutter_open_pairs.
        reopen = dict(shutter_open_pairs(capability))
        for offset, ranges in capability.capabilities_for_role(roles.STROBE):
            strobe = _named(ranges, "strobe")
            if strobe is None:
                continue
            strobing.append((offset, strobe.middle))
            opening.append((offset, reopen.get(offset, 0)))
        if strobing:
            result[capability.fixture.fixture_id] = (strobing, opening)
    return result


def _named(ranges, needle: str):
    for capability in ranges:
        if needle in capability.name.lower():
            return capability
    return None


def _scene(workspace: Workspace, name: str, values, path: str) -> int:
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id


def _flash_chaser(
    workspace: Workspace, name: str, full_id: int, black_id: int,
    hold: int, path: str,
) -> int:
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(function_id, name, [full_id, black_id], hold=hold, path=path)
    )
    return function_id
