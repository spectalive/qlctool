"""Scenes for the effects a fixture runs by itself, one per programme.

The HYULIGHTS panels carry forty-two built-in animations and this show used
none of them: their mode channel sat at "No function", so four rather clever
little lights spent every night as four RGB cells. Each scene here switches the
mode channel into its automatic position, picks one programme, sets the speed
and opens the intensity - everything the fixture needs to be left alone.

Nobody knows what the forty-two look like. The definition names them "Effect 1"
to "Effect 42" and there is no manual in the repo, so they are all generated and
all put on the console: the way to find out is to stand in front of them once.
The chaser is deliberately slow for the same reason - an effect nobody has seen
should be given long enough to be seen.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import roles
from ..capability import FixtureCapabilities
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..internal_program import internal_program
from ..shutter_open import shutter_open_pairs
from ..zoom_wide import zoom_wide_pairs
from ..strobe_off import strobe_off_pairs
from ..workspace import Workspace

PATH = "Efectos Propios"
# Where the hand-built show ran these: its speed sequence stepped the panels'
# channel between 160 and 255, so 128 - the blind mid-scale first guess - was
# slower than the show had ever actually looked. 200 sits in the middle of the
# range the room is known to have worked at (audit of DeluxeEventos2's
# "Strobo LED" functions, 2026-08-27).
DEFAULT_SPEED = 200

# Programmes generated but left out of the cycle, 1-based. Effect 40 is a
# number counter - the one programme the hand-built show's own chaser skipped
# (its "Strobo LED - Effects" steps 41 of the 42, and the owner confirms:
# "estaban todos menos uno que va como con un contador de numeros",
# 2026-08-28). Its scene still exists for the library page; a counter is a
# thing to show somebody once, not a look for a party.
EXCLUDED_FROM_CYCLE = (40,)


@dataclass(frozen=True)
class GeneratedBuiltins:
    scene_ids: list[int] = field(default_factory=list)
    chaser_id: int | None = None
    fixture_ids: tuple[int, ...] = ()
    # (fixture id, channel offset) of every speed channel the scenes set, so
    # the console can put a live fader over them the way the hand-built show
    # did ("Strobo LED Effect Speed").
    speed_channels: tuple[tuple[int, int], ...] = ()


def generate_builtin_effects(
    workspace: Workspace,
    capabilities: Sequence[FixtureCapabilities],
    label: str,
    speed: int = DEFAULT_SPEED,
    hold: int = 12000,
    run_order: str = "Random",
    path: str = PATH,
) -> GeneratedBuiltins:
    """A scene per built-in programme, plus a chaser walking them.

    Every fixture that has programmes runs the *same* one in each scene, so the
    four panels animate together rather than each doing its own thing.
    """
    programmed = [
        (capability, program)
        for capability in capabilities
        if not capability.is_smoke
        and (program := internal_program(capability)) is not None
    ]
    if not programmed:
        return GeneratedBuiltins()

    # The shortest list wins, so no scene asks a fixture for a programme it
    # does not have.
    count = min(program.count for _, program in programmed)

    scene_ids: list[int] = []
    for index in range(count):
        values: dict[int, list[tuple[int, int]]] = {}
        for capability, program in programmed:
            pairs = [
                (program.mode_offset, program.auto_value),
                (program.effect_offset, program.effects[index].middle),
            ]
            if program.speed_offset is not None:
                pairs.append((program.speed_offset, speed))
            pairs += [
                (offset, 255)
                for offset in capability.offsets_for_role(roles.DIMMER)
            ]
            pairs += shutter_open_pairs(capability)
            pairs += zoom_wide_pairs(capability)
            # A strobe-only channel is LTP and a released Flash restores
            # nothing: the scene that owns the light writes the strobe off.
            pairs += strobe_off_pairs(capability)
            values[capability.fixture.fixture_id] = pairs

        function_id = next_function_id(workspace.root)
        name = programmed[0][1].effects[index].name.strip() or f"Efecto {index + 1}"
        workspace.add_function(
            build_scene(function_id, f"{label} - {name}", values, path=path)
        )
        scene_ids.append(function_id)

    cycled = [
        scene_id
        for index, scene_id in enumerate(scene_ids, start=1)
        if index not in EXCLUDED_FROM_CYCLE
    ]
    chaser_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            chaser_id,
            f"Ciclo {label}",
            cycled,
            hold=hold,
            run_order=run_order,
            path=path,
        )
    )
    return GeneratedBuiltins(
        scene_ids=scene_ids,
        chaser_id=chaser_id,
        fixture_ids=tuple(c.fixture.fixture_id for c, _ in programmed),
        speed_channels=tuple(
            (capability.fixture.fixture_id, program.speed_offset)
            for capability, program in programmed
            if program.speed_offset is not None
        ),
    )
