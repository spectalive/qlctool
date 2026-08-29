"""A beam figure that leaves the part of the room the audience is in.

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

Only EFX are asked. A Scene that aims the heads somewhere on purpose - the
hand-built `Escenario`, which sits just below the window at tilt 189-204
because the stage is not the crowd - is a decision, not a figure.
"""

from .. import roles
from ..audience_window import BEAM_WINDOW
from ..xmlutil import find_local, findall_local
from .driven_channels import EFX_PAN_TILT
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "figura fuera del publico"


def check_beam_window(graph: ShowGraph) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        if function.attrib.get("Type") != "EFX":
            continue
        beams = _beams_moved(graph, function)
        if not beams:
            continue
        width = _number(function, "Width")
        height = _number(function, "Height")
        pan = _axis_offset(function, "X")
        tilt = _axis_offset(function, "Y")
        if None in (width, height, pan, tilt):
            continue
        outside = [
            f"{axis} {centre - size}..{centre + size}"
            for axis, centre, size in (
                ("pan", pan, width), ("tilt", tilt, height)
            )
            if not BEAM_WINDOW.holds(centre, size, axis)
        ]
        if not outside:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=ERROR,
            function=graph.name(function_id),
            message=(
                f"dibuja {', '.join(outside)}, y el publico esta en pan "
                f"{BEAM_WINDOW.pan_min}-{BEAM_WINDOW.pan_max} tilt "
                f"{BEAM_WINDOW.tilt_min}-{BEAM_WINDOW.tilt_max}: parte de la "
                "figura apunta fuera de la sala"
            ),
            fixtures=tuple(sorted(beams)),
        ))
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


def _beams_moved(graph: ShowGraph, function) -> set[str]:
    """The beam-class fixtures this EFX drives on pan and tilt."""
    beams: set[str] = set()
    for element in findall_local(function, "Fixture"):
        identifier = find_local(element, "ID")
        if identifier is None or not (identifier.text or "").strip().isdigit():
            continue
        mode = find_local(element, "Mode")
        mode_value = (
            int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT
        )
        if mode_value != EFX_PAN_TILT:
            continue
        capability = graph.capabilities.get(int(identifier.text))
        if capability is None or not capability.has_role(roles.GOBO):
            continue
        beams.add(capability.fixture.name)
    return beams
