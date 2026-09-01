"""A figure centred on mid-travel, which is where an unaimed figure lands.

2026-08-29, one night, both families: "está todo el rato haciendo un circulo
pequeño en el suelo" (the beams) and "los washes apuntan para atrás a la pared,
que no me interesa iluminar". Every movement EFX this repo had ever generated
carried QLC+'s own axis default - `<Axis Name="Y"><Offset>127`, the raw middle
of the tilt channel - because `EFXAxis.offset` defaults there and no generator
had ever overridden it. The old hand-built show was no better aimed; it got
away with it by drawing figures 100 wide, so the sweep crossed the room on its
way past whatever mid-travel pointed at.

Mid-travel is not an aim. It is the number you get when nobody chose, and where
it lands is per model, not per rig: on the 7R it is the floor, on the washes it
is the wall behind the stage. Both anchored by the hand-built show and by what
the owner saw - see `generate/movement_aim`.

Asked of anything an EFX moves on pan and tilt. A wash's wide cone is more
forgiving than a 2-degree needle, but neither of them is aimed by a default.
"""

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
        heads = _heads_moved(graph, function)
        if not heads:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=WARNING,
                function=graph.name(function_id),
                message=(
                    f"dibuja la figura centrada en el tilt {MID_TRAVEL}, que es el "
                    "centro del recorrido y no un sitio: es donde queda una figura "
                    "que nadie ha apuntado - el suelo en las 7R, la pared del fondo "
                    "en los washes"
                ),
                fixtures=tuple(sorted(heads)),
            )
        )
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


def _heads_moved(graph: ShowGraph, function) -> set[str]:
    """The fixtures this EFX drives on pan and tilt."""
    heads: set[str] = set()
    for element in findall_local(function, "Fixture"):
        identifier = find_local(element, "ID")
        if identifier is None or not (identifier.text or "").strip().isdigit():
            continue
        mode = find_local(element, "Mode")
        mode_value = int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT
        if mode_value != EFX_PAN_TILT:
            continue
        capability = graph.capabilities.get(int(identifier.text))
        if capability is None:
            continue
        heads.add(capability.fixture.name)
    return heads
