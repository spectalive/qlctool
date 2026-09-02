"""Strobes, of the two kinds this rig can actually do.

A fixture with a shutter strobes itself: one channel value and it keeps
flashing. Only the fixtures whose definition *labels* a strobe range get driven
here - a MiN Wash's shutter channel puts "Closed" at 1-7, so guessing a value on
an unlabelled channel is how a head goes dark in the middle of a set.

Everything else - the LED bars - has no shutter at all, and nothing in QLC+
can blink it to black on top of a lit state. The first STROBO was a chaser
flipping the rig between a white scene and a black one: the black step wrote
zeros to dimmers and RGB, every one of them an Intensity channel, and Intensity
is HTP - under any room state the state's own dimmer at 255 wins the compare
(`Universe::write`), so the "black" half of the strobe changed nothing. The
room saw white / state-colour, never white / black, and on the four BEAM 7R
the colour wheel was commanded white and back every 125 ms (cross-audit,
2026-09-02). It only ever worked under `Todo Negro`, which is the one state
nobody strobes.

So the two console strobes are the honest shape: a held Flash scene driving
every strobe-capable channel at a rate, colour and dimmers left to the state -
the same wiring as `Flash Color`, at the two speeds the buttons promise. A
fixture with no strobe channel is not in them, because it cannot strobe.

`Strobo ON` / `Strobo OFF` stay as the latched pair for somebody who wants the
shutters going for a while.
"""

from dataclasses import dataclass

from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..shutter_open import shutter_open_pairs
from ..strobe_speed import strobe_speed_pairs
from ..workspace import Workspace

# Where the held strobes sit on each channel's slow-to-fast run: the same two
# points the flashes use - 0.97 is the owner's "246-248" on the PARs and
# 0.785 the "unos 200" of the slow one (2026-08-29). `flash lento` refuses a
# held strobe below 70% of the run. The latched `Strobo ON` keeps the midpoint.
FAST_FRACTION = 0.97
MEDIUM_FRACTION = 0.785
ON_FRACTION = 0.5


@dataclass(frozen=True)
class GeneratedStrobes:
    on_id: int | None
    off_id: int | None
    fast_id: int
    medium_id: int


def generate_strobe_effects(
    workspace: Workspace,
    library: FixtureLibrary,
    path: str = "Strobos",
) -> GeneratedStrobes:
    """The latched shutter pair plus the two held strobe scenes."""
    shutter = _shutter_values(workspace, library)
    on_id = off_id = None
    if shutter:
        on_id = _scene(workspace, "Strobo ON", {f: v for f, (v, _) in shutter.items()}, path)
        off_id = _scene(workspace, "Strobo OFF", {f: v for f, (_, v) in shutter.items()}, path)
    fast_id = _scene(workspace, "Strobo Rapido", _held_values(workspace, library, FAST_FRACTION), path)
    medium_id = _scene(
        workspace, "Strobo Medio", _held_values(workspace, library, MEDIUM_FRACTION), path
    )
    return GeneratedStrobes(on_id=on_id, off_id=off_id, fast_id=fast_id, medium_id=medium_id)


def _held_values(workspace: Workspace, library: FixtureLibrary, fraction: float):
    """Fixture id -> every strobe channel at `fraction`, nothing else."""
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities_of(workspace.root, library):
        if capability.is_smoke:
            continue
        strobing = strobe_speed_pairs(capability, fraction)
        if strobing:
            values[capability.fixture.fixture_id] = sorted(strobing)
    return values


def _shutter_values(workspace: Workspace, library: FixtureLibrary):
    """Fixture id -> (values that strobe it, values that reopen it).

    The strobing value through `strobe_speed_pairs`, which also covers the
    channels whose whole job is the strobe and carry no labelled range at all
    (the Vortex PC-64, the HYULIGHTS panels) - leaving those out is how
    `Strobo ON` shipped strobing ten fixtures and skipping nine (found live,
    2026-08-27). The reopen value through `shutter_open_pairs`, so a strobe
    that stops and a scene that opens a shutter always agree on where "open"
    is; a channel with no labelled open position reopens at 0, which is where
    the untouched channel already sat.
    """
    result: dict[int, tuple[list[tuple[int, int]], list[tuple[int, int]]]] = {}
    for capability in capabilities_of(workspace.root, library):
        if capability.is_smoke:
            continue
        reopen = dict(shutter_open_pairs(capability))
        strobing = strobe_speed_pairs(capability, ON_FRACTION)
        opening = [(offset, reopen.get(offset, 0)) for offset, _ in strobing]
        if strobing:
            result[capability.fixture.fixture_id] = (strobing, opening)
    return result


def _scene(workspace: Workspace, name: str, values, path: str) -> int:
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
