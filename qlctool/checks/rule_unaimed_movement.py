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

from .efx_pan_tilt_fixture_names import efx_pan_tilt_fixture_names
from .efx_tilt_offset import efx_tilt_offset
from .finding import WARNING, Finding
from .show_graph import ShowGraph

RULE_ID = "unaimed_movement"
# The raw middle of an 8-bit channel, which is what QLC+ writes by default.
MID_TRAVEL = 127


def check_unaimed_movement(graph: ShowGraph) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        if function.attrib.get("Type") != "EFX":
            continue
        if efx_tilt_offset(function) != MID_TRAVEL:
            continue
        heads = efx_pan_tilt_fixture_names(graph, function)
        if not heads:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=WARNING,
                function=graph.name(function_id),
                message_id="unaimed_movement_mid_tilt",
                fields={"tilt": MID_TRAVEL},
                fixtures=tuple(sorted(heads)),
            )
        )
    return findings
