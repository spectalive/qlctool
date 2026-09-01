"""Strobes, of the two kinds this rig can actually do.

A fixture with a shutter strobes itself: one channel value and it keeps
flashing. Only the fixtures whose definition *labels* a strobe range get driven
here - a MiN Wash's shutter channel puts "Closed" at 1-7, so guessing a value on
an unlabelled channel is how a head goes dark in the middle of a set.

Everything else - the LED bars and PARs - has no shutter, so it strobes the way
the hand-built show does it: a chaser flipping the whole rig between full and
black. Two speeds, because one is a hard strobe and the other is a pulse.

Both chasers are **bounded bursts, capped at 4 Hz** (2026-08-27). The first
version looped at 50 ms a step - ten flashes a second, inside the
photosensitive-epilepsy trigger band, latched behind a Toggle button. UK
performance guidance caps effect flashing at four per second, and QLC+ cannot
make a chaser momentary (only Scenes flash), so the safe shape is a SingleShot
chaser: press it, it plays its pulses, it stops on its own.
"""

from dataclasses import dataclass

from ..capabilities_of import capabilities_of
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..shutter_open import shutter_open_pairs
from ..strobe_speed import strobe_speed_pairs
from ..workspace import Workspace

# Half-cycles: full for this long, black for this long. 125 ms each way is
# 4 Hz - the cap - and 250 ms is a 2 Hz pulse.
FAST_MS = 125
MEDIUM_MS = 250
# One press is one burst: this many flashes, then the chaser ends itself.
PULSES = 4
# Where `Strobo ON` sits on each shutter's slow-to-fast run. Mid-speed: it is
# a latched look somebody walks away from, not a hit.
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
    medium_id = _flash_chaser(workspace, "Strobo Medio", full_id, black_id, MEDIUM_MS, path)
    return GeneratedStrobes(on_id=on_id, off_id=off_id, fast_id=fast_id, medium_id=medium_id)


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
        # One source of truth for "what value opens this shutter": the range the
        # definition marks `ShutterOpen`, read by shutter_open_pairs.
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


def _flash_chaser(
    workspace: Workspace,
    name: str,
    full_id: int,
    black_id: int,
    hold: int,
    path: str,
) -> int:
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            function_id,
            name,
            [full_id, black_id] * PULSES,
            hold=hold,
            run_order="SingleShot",
            path=path,
        )
    )
    return function_id
