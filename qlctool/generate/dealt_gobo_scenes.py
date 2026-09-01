"""Four beams, four different gobos, walking one seat along on every step.

The gobo wheel had exactly one look on it: every beam on the same pattern,
seventeen of them in a row. That is a slideshow, not a rig - "los beam quedaron
bien posicionados pero le faltaba usar mas los gobos los prismas etc, no se
como lo usan los pros pero se echaba en falta mas variedad" (owner,
2026-08-30). What a professional room does with four heads and one wheel is
deal them: each head on its own pattern, all four turning over together, so the
picture is four shapes crossing instead of one shape repeated.

Same arithmetic as `dealt_wheel_color` does for colour: beam *i* sits `i` seats
along the wheel from the step's own start, so neighbours always differ and
every head lands on a real detent. The wheel's blank position ("White Light")
is skipped - a deal is about patterns, and an open beam in the middle of one
reads as a head that failed.
"""

from collections.abc import Sequence

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace

# How many deals to generate. Eight is two full turns of the four heads through
# the wheel's seventeen patterns: long enough that the room never sees the same
# four-shape picture twice inside one party level.
DEALS = 8
# The blank position every gobo wheel opens with, by preset: the beam with no
# pattern in it.
OPEN_PRESETS = ("GoboMacro",)
OPEN_NAMES = ("white light", "open", "no gobo")


def generate_dealt_gobo_scenes(
    workspace: Workspace,
    library: FixtureLibrary,
    companions: Sequence[tuple[str, int]] = (),
    path: str = "Gobos",
) -> list[int]:
    """One scene per deal, or an empty list when the rig has no gobo wheel.

    companions are (role, value) pairs every scene writes on those same
    fixtures - the focus that makes a pattern a pattern, the shake parked at
    zero - for the same reason the plain gobo scenes carry them: the channels
    are LTP and keep whatever the last look left there.
    """
    beams = sorted(
        (
            capability
            for capability in capabilities_of(workspace.root, library)
            if capability.has_role(roles.GOBO)
        ),
        key=lambda capability: capability.fixture.address,
    )
    if not beams:
        return []
    _, positions = beams[0].wheel_for_role(roles.GOBO)
    patterns = [
        position
        for position in positions
        if (position.name or "").strip().lower() not in OPEN_NAMES
        and (position.preset or "") in OPEN_PRESETS
    ]
    if len(patterns) < len(beams):
        return []

    scene_ids: list[int] = []
    for deal in range(DEALS):
        values: dict[int, list[tuple[int, int]]] = {}
        for seat, capability in enumerate(beams):
            offset, _ = capability.wheel_for_role(roles.GOBO)
            pattern = patterns[(deal * len(beams) + seat) % len(patterns)]
            pairs = [(offset, pattern.middle)]
            for role, value in companions:
                pairs += [
                    (companion_offset, value)
                    for companion_offset in capability.offsets_for_role(role)
                ]
            values[capability.fixture.fixture_id] = pairs
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_scene(
                function_id,
                f"Gobo Repartido {deal + 1}",
                values,
                path=path,
            )
        )
        scene_ids.append(function_id)
    return scene_ids
