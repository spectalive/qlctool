"""A movement figure that leaves the part of the room the audience is in.

The aim was guessed twice on 2026-08-29 and was wrong twice - the beams drew a
circle on the floor, then pointed at the wall behind - because "which way is
up" was being inferred from other fixtures' numbers instead of read off this
one. The owner ended it by putting BEAM 230W 7R #1 on the desk and sending the
corners: pan 62 to 103, tilt 207 to 234, "todo lo fuera de eso ya apunta a
fuera" (`audience_window`).

With a window written down, the question stops being a matter of taste. An EFX
draws a shape of a known half-size around a known centre - both are in the file
- so whether the whole shape stays on the people is arithmetic:
`offset - size` and `offset + size`, per axis, inside the window.

Each family is asked about its own window: a raw pan or tilt value means
nothing across models, and the washes were measured separately (pan 76-108,
tilt 212-230 on MAC WASH 1915Z #1).

Only EFX are asked. A Scene that aims the heads somewhere on purpose - the
hand-built `Escenario`, which sits just below the window at tilt 189-204
because the stage is not the crowd - is a decision, not a figure.
"""

from .. import roles
from ..audience_window import BEAM_WINDOW, WASH_WINDOW
from ..xmlutil import find_local, findall_local
from .driven_channels import EFX_PAN_TILT
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "figura fuera del publico"


def check_movement_window(graph: ShowGraph) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        if function.attrib.get("Type") != "EFX":
            continue
        moved = _heads_by_family(graph, function)
        if not moved:
            continue
        width = _number(function, "Width")
        height = _number(function, "Height")
        pan = _axis_offset(function, "X")
        tilt = _axis_offset(function, "Y")
        if None in (width, height, pan, tilt):
            continue
        for window, names in moved.items():
            outside = [
                f"{axis} {centre - size}..{centre + size}"
                for axis, centre, size in (("pan", pan, width), ("tilt", tilt, height))
                if not window.holds(centre, size, axis)
            ]
            if not outside:
                continue
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        f"dibuja {', '.join(outside)}, y el publico esta en pan "
                        f"{window.pan_min}-{window.pan_max} tilt "
                        f"{window.tilt_min}-{window.tilt_max}: parte de la figura "
                        "apunta fuera de la sala"
                    ),
                    fixtures=tuple(sorted(names)),
                )
            )
    return findings


def _number(function, name: str) -> int | None:
    element = find_local(function, name)
    if element is None or not (element.text or "").strip().lstrip("-").isdigit():
        return None
    return int(element.text)


def _axis_offset(function, name: str) -> int | None:
    for axis in findall_local(function, "Axis"):
        if axis.attrib.get("Name") != name:
            continue
        return _number(axis, "Offset")
    return None


def _heads_by_family(graph: ShowGraph, function) -> dict:
    """The fixtures this EFX moves, grouped by the window their family lives in.

    Told apart the way `rule_movement_families` tells them: a mover with a gobo
    wheel is a beam, one without is a wash. They are different windows because
    a raw pan or tilt value means nothing across models.
    """
    moved: dict = {}
    for element in findall_local(function, "Fixture"):
        identifier = find_local(element, "ID")
        if identifier is None or not (identifier.text or "").strip().isdigit():
            continue
        mode = find_local(element, "Mode")
        mode_value = int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT
        if mode_value != EFX_PAN_TILT:
            continue
        capability = graph.capabilities.get(int(identifier.text))
        if capability is None or capability.is_smoke:
            continue
        window = BEAM_WINDOW if capability.has_role(roles.GOBO) else WASH_WINDOW
        moved.setdefault(window, set()).add(capability.fixture.name)
    return moved
