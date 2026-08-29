"""A rig-wide colour that spins a colour wheel instead of naming a position.

2026-08-29, live under AUTO: "las 7R no se abren del todo, están como una media
luna". Nothing was closed. `Rig Multicolor 1` and `Rig Multicolor 2` - two of
the twenty steps of the colour clock, so the fault arrived "a veces" - sent the
BEAM 230W 7R's colour wheel to 186, inside its `RotationClockwiseFastToSlow`
range, and near the slow end of it. A rotation range is not a colour: the wheel
turns, and a 2-degree beam looking through a wheel that is between two detents
shows half of one colour and half of the next. At the slow end it stays there.

The rule reasons about what the look claims. A scene that states a colour on
the RGB fixtures has made a claim about the whole rig, and a wheel fixture in
that claim has to land on a position the wheel actually carries. A scene that
writes nothing but one wheel - the per-position library scenes, where "Rainbow
effect fast to slow" is the point and the operator asked for it by name - makes
no such claim and is left alone.
"""

from .. import roles
from .color_roles import COLOUR
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit, reach

RULE = "rueda de color girando"
STATES_COLOUR = ("Scene", "Sequence")
ROTATION_PRESET_PREFIX = "Rotation"


def check_wheel_rotation(graph: ShowGraph, groups) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        if graph.kind(function_id) not in STATES_COLOUR:
            continue
        stated = reach(graph, groups, function_id, kinds=STATES_COLOUR)
        if not _states_rgb_colour(graph, stated):
            continue
        spinning = sorted(_spinning_wheels(graph, stated))
        if spinning:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                message=(
                    "da color a todo el rig pero deja la rueda de color de "
                    "estos fixtures en un rango de giro, que no es un color: "
                    "la rueda queda entre dos posiciones y el haz sale a medias "
                    "(media luna)"
                ),
                fixtures=tuple(spinning),
            ))
    return findings


def _states_rgb_colour(graph: ShowGraph, stated) -> bool:
    """Whether this scene says a colour on a fixture that has red, green, blue."""
    for fixture_id, written in stated.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke or not written:
            continue
        if not any(
            capability.has_role(role)
            for role in (roles.RED, roles.GREEN, roles.BLUE)
        ):
            continue
        offsets = {o for role in COLOUR for o in capability.offsets_for_role(role)}
        if any(lit(written[o]) for o in offsets if o in written):
            return True
    return False


def _spinning_wheels(graph: ShowGraph, stated) -> set[str]:
    """The wheel-coloured fixtures this scene parks on a rotation range."""
    spinning: set[str] = set()
    for fixture_id, written in stated.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke or not written:
            continue
        if any(
            capability.has_role(role)
            for role in (roles.RED, roles.GREEN, roles.BLUE)
        ):
            continue
        wheel = capability.wheel_for_role(roles.COLOR_MACRO)
        if wheel is None:
            continue
        offset, positions = wheel
        value = written.get(offset)
        if value is None:
            continue
        if _is_rotation(positions, value):
            spinning.add(capability.fixture.name)
    return spinning


def _is_rotation(positions, value: int) -> bool:
    """Whether the range holding this value spins the wheel rather than naming."""
    for position in positions:
        if position.minimum <= value <= position.maximum:
            return (position.preset or "").startswith(ROTATION_PRESET_PREFIX)
    return False
