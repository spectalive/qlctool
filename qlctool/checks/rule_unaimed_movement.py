"""A beam figure centred on mid-travel, which is where an unaimed figure lands.

2026-08-29: "está todo el rato haciendo un circulo pequeño en el suelo". Every
movement EFX this repo had ever generated carried QLC+'s own axis default -
`<Axis Name="Y"><Offset>127`, the raw middle of the tilt channel - because
`EFXAxis.offset` defaults there and no generator had ever overridden it. The
old hand-built show was no better aimed; it got away with it by drawing figures
100 wide, so the sweep crossed the room on its way past the floor.

Mid-travel is not an aim. It is the number you get when nobody chose, and on
this rig it is the floor: tilt 0 is the ceiling (a CromoWash stuck at coarse
zero "sat pointing at the ceiling", `docs/rig.md`), tilt ~196 is the stage
(the hand-built `Escenario`), and the audience lives below 127.

Asked of the beam family only, and told apart the way `rule_movement_families`
tells it - a mover with a gobo wheel is a beam. A wash's wide cone at mid
travel still lights a room; a 2-degree needle at mid travel is a coin on the
floor, and the narrower the optics the more the aim is the whole look.
"""

from .. import roles
from ..xmlutil import find_local, findall_local
from .driven_channels import EFX_PAN_TILT
from .finding import WARNING, Finding
from .show_graph import ShowGraph

RULE = "movimiento sin apuntar"
# The raw middle of an 8-bit channel, which is what QLC+ writes by default.
MID_TRAVEL = 127


def check_unaimed_movement(graph: ShowGraph) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        if function.attrib.get("Type") != "EFX":
            continue
        if _tilt_offset(function) != MID_TRAVEL:
            continue
        beams = _beams_moved(graph, function)
        if not beams:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=WARNING,
            function=graph.name(function_id),
            message=(
                f"dibuja la figura centrada en el tilt {MID_TRAVEL}, que es el "
                "centro del recorrido y no un sitio: es donde queda una figura "
                "que nadie ha apuntado, y en este rig es el suelo"
            ),
            fixtures=tuple(sorted(beams)),
        ))
    return findings


def _tilt_offset(function) -> int | None:
    """The centre of the EFX's Y axis, which is the tilt one."""
    for axis in findall_local(function, "Axis"):
        if axis.attrib.get("Name") != "Y":
            continue
        offset = find_local(axis, "Offset")
        if offset is None or not (offset.text or "").strip().lstrip("-").isdigit():
            return None
        return int(offset.text)
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
