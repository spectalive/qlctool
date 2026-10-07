"""A movement figure that leaves the part of the room the audience is in.

The aim was guessed twice on 2026-08-29 and was wrong twice - the beams drew a
circle on the floor, then pointed at the wall behind - because "which way is
up" was being inferred from other fixtures' numbers instead of read off this
one. The owner ended it by putting BEAM 230W 7R #1 on the desk and sending the
corners: pan 62 to 103, tilt 207 to 234, "todo lo fuera de eso ya apunta a
fuera" (`audience_windows`).

With a window written down, the question stops being a matter of taste. An EFX
draws a known shape of a known size, turned by a known angle, around a known
centre - all of it is in the file - so whether the whole shape stays on the
people is arithmetic: the figure's reach per axis (`efx_extent`, QLC+'s own
`calculatePoint` and `rotateAndScale`), added to the offset, inside the window.

The reach used to be read as `offset +- Width` on pan and `offset +- Height`
on tilt, which is only true at Rotation 0. Turned 90 degrees, a Diamond of
Width 20 and Height 13 swings tilt by 20, and every Diamante put the 7R at tilt
200-240 about 30% of the time - past a window of 207-234 - while the rule
passed it (en-sala DMX re-audit, 2026-09-27).

Each family is asked about its own window: a raw pan or tilt value means
nothing across models, and the washes were measured separately (pan 76-108,
tilt 212-230 on MAC WASH 1915Z #1).

Only EFX are asked. A Scene that aims the heads somewhere on purpose - the
hand-built `Escenario`, which sits just below the window at tilt 189-204
because the stage is not the crowd - is a decision, not a figure.
"""

import math

from ..efx_extent import efx_extent
from ..find_local import find_local
from .axis_offset import axis_offset
from .axis_shape import axis_shape
from .finding import ERROR, Finding
from .function_number import function_number
from .heads_by_family import heads_by_family
from .reach_count import reach_count
from .show_graph import ShowGraph

RULE_ID = "movement_window"

# Sampling lands on the exact extremes up to float noise; a figure drawn to the
# window's edge is inside it.
_TOLERANCE = 1e-6


def check_movement_window(graph: ShowGraph) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        if function.attrib.get("Type") != "EFX":
            continue
        moved = heads_by_family(graph, function)
        if not moved:
            continue
        width = function_number(function, "Width")
        height = function_number(function, "Height")
        pan = axis_offset(function, "X")
        tilt = axis_offset(function, "Y")
        if width is None or height is None or pan is None or tilt is None:
            continue
        algorithm = find_local(function, "Algorithm")
        rotation = function_number(function, "Rotation")
        x_frequency, x_phase = axis_shape(function, "X", 2, 90)
        y_frequency, y_phase = axis_shape(function, "Y", 3, 0)
        pan_reach, tilt_reach = efx_extent(
            (algorithm.text or "").strip() if algorithm is not None else "Circle",
            width,
            height,
            min(max(rotation or 0, 0), 359),
            x_frequency,
            y_frequency,
            math.radians(x_phase),
            math.radians(y_phase),
        )
        for window, names in moved.items():
            outside = [
                f"{axis} {reach_count(centre + low)}..{reach_count(centre + high)}"
                for axis, centre, (low, high), (window_min, window_max) in (
                    ("pan", pan, pan_reach, (window.pan_min, window.pan_max)),
                    ("tilt", tilt, tilt_reach, (window.tilt_min, window.tilt_max)),
                )
                if centre + low < window_min - _TOLERANCE or centre + high > window_max + _TOLERANCE
            ]
            if not outside:
                continue
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message_id="movement_window_outside",
                    fields={
                        "outside": ", ".join(outside),
                        "pan_min": window.pan_min,
                        "pan_max": window.pan_max,
                        "tilt_min": window.tilt_min,
                        "tilt_max": window.tilt_max,
                    },
                    fixtures=tuple(sorted(names)),
                )
            )
    return findings
