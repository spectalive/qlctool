"""Gobo shake bursts: the pattern trembling in the haze for a peak.

The 7R's Pattern Jitter channel shakes whatever gobo is in the beam - the
pro move for a drop, where a still pattern reads as wallpaper and a shaken one
reads as a hit. A shake is only ever a step of the gobo wheel's own rotation,
never a concurrent layer: two functions writing the jitter channel at once
fight LTP every tick, so the plain gobo scenes park the shake at zero (their
companion write) and these steps are the one place it comes on.

Three bursts, evenly spaced across the wheel's patterns, each stating its own
gobo: a shake with no gobo inserted shakes an open beam, which shows nothing.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace

# Mid-speed on the jitter's 1-128 slow-to-fast run: visible tremble, not blur.
SHAKE_VALUE = 64
BURSTS = 3
GOBO_POSITION_PRESET = "GoboMacro"


@dataclass(frozen=True)
class GeneratedGoboShake:
    scene_ids: list[int] = field(default_factory=list)


def generate_gobo_shake(
    workspace: Workspace,
    library: FixtureLibrary,
    path: str = "Gobos",
) -> GeneratedGoboShake:
    """Shake scenes over every fixture that has both a gobo wheel and a shake."""
    caps = [
        c for c in capabilities_of(workspace.root, library)
        if c.has_role(roles.GOBO) and c.has_role(roles.GOBO_SHAKE)
    ]
    if not caps:
        return GeneratedGoboShake()

    # Pattern positions come from the first fixture: they share the wheel.
    _, positions = caps[0].wheel_for_role(roles.GOBO)
    patterns = [
        p for p in positions
        if (p.preset or "") == GOBO_POSITION_PRESET and p is not positions[0]
    ]
    if not patterns:
        return GeneratedGoboShake()
    chosen = _spaced(patterns, BURSTS)

    scene_ids: list[int] = []
    for position in chosen:
        values: dict[int, list[tuple[int, int]]] = {}
        for capability in caps:
            offset, _ = capability.wheel_for_role(roles.GOBO)
            pairs = [(offset, position.middle)]
            pairs += [
                (shake_offset, SHAKE_VALUE)
                for shake_offset in capability.offsets_for_role(roles.GOBO_SHAKE)
            ]
            values[capability.fixture.fixture_id] = pairs
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(
            function_id, f"Gobo Shake - {position.name}", values, path=path
        ))
        scene_ids.append(function_id)
    return GeneratedGoboShake(scene_ids=scene_ids)


def _spaced(patterns: Sequence, count: int) -> list:
    """`count` positions spread evenly across the wheel's patterns."""
    if len(patterns) <= count:
        return list(patterns)
    return [patterns[round(i * (len(patterns) - 1) / (count - 1))] for i in range(count)]
