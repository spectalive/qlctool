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

from .finding import ERROR, Finding
from .reach import reach
from .show_graph import ShowGraph
from .spinning_wheels import spinning_wheels
from .states_rgb_colour import states_rgb_colour

RULE_ID = "wheel_rotation"
STATES_COLOUR = ("Scene", "Sequence")


def check_wheel_rotation(graph: ShowGraph, groups: dict[int, tuple[int, ...]]) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        if graph.kind(function_id) not in STATES_COLOUR:
            continue
        stated = reach(graph, groups, function_id, kinds=STATES_COLOUR)
        if not states_rgb_colour(graph, stated):
            continue
        spinning = sorted(spinning_wheels(graph, stated))
        if spinning:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message_id="wheel_rotation_spinning",
                    fixtures=tuple(spinning),
                )
            )
    return findings
