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

from .. import roles
from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..functions.build_scene import build_scene
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .generated_gobo_shake import GeneratedGoboShake
from .spaced import spaced

# Mid-speed on the jitter's 1-128 slow-to-fast run: visible tremble, not blur.
SHAKE_VALUE = 64
BURSTS = 3
GOBO_POSITION_PRESET = "GoboMacro"


def generate_gobo_shake(
    workspace: Workspace,
    library: FixtureLibrary,
    companions: Sequence[tuple[str, int]] = (),
    path: str = "Gobos",
) -> GeneratedGoboShake:
    """Shake scenes that also own every supplied gobo companion channel."""
    caps = [
        c
        for c in capabilities_of(workspace.root, library)
        if c.has_role(roles.GOBO) and c.has_role(roles.GOBO_SHAKE)
    ]
    if not caps:
        return GeneratedGoboShake()

    # Pattern positions come from the first fixture: they share the wheel.
    _, positions = caps[0].wheel_for_role(roles.GOBO)
    patterns = [
        p for p in positions if (p.preset or "") == GOBO_POSITION_PRESET and p is not positions[0]
    ]
    if not patterns:
        return GeneratedGoboShake()
    chosen = spaced(patterns, BURSTS)

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
            for role, value in companions:
                pairs += [
                    (companion_offset, value)
                    for companion_offset in capability.offsets_for_role(role)
                ]
            values[capability.fixture.fixture_id] = pairs
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_scene(function_id, f"Gobo Shake - {position.name}", values, path=path)
        )
        scene_ids.append(function_id)
    return GeneratedGoboShake(scene_ids=scene_ids)
