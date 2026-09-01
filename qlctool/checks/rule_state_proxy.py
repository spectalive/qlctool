"""A chaser that presses the room's state buttons without a hand near them.

2026-08-29, the owner pressing the strobes: "strobo y strobo suave alternan
entre parar y apagon y luego se para el show". The burst chasers stepped
`Blanco Total` and `Todo Negro` - the very functions bound to the room-state
solo frame's buttons. In qmlui a Toggle button hears its function start no
matter who started it (`VCButton::slotFunctionRunning` emits
`functionStarting`), and the solo frame answers a member starting by stopping
every other member - so each pulse of the chaser pressed BLANCO TOTAL, then
TODO NEGRO, killed AUTO on the first step, and left the room stopped when the
burst ended. The same wiring had already bitten once from the other side: the
bass bar pressing `Blanco Total` stopped AUTO (2026-08-27), which is why
`Golpe Graves` exists.

The rule: no function may start, as a step or member, a function that is one
of the room's states. The states are found by `room_states` - the solo frame
whose buttons between them drive the whole rig - never by name. A function
that wants a state's look builds its own twin scene; a twin with a different
function id presses no button.
"""

from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "estado pulsado por otra funcion"


def check_state_proxy(graph: ShowGraph, states: set[int]) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, members in sorted(graph.members.items()):
        pressed = sorted(
            {member for member in members if member in states and member != function_id}
        )
        for state_id in pressed:
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        f"arranca «{graph.name(state_id)}», que es un boton del "
                        f"marco de estados de la sala: el boton se entera aunque "
                        f"lo arranque un chaser (qmlui "
                        f"VCButton::slotFunctionRunning) y el solo frame para el "
                        f"estado que estuviera sonando - el show se muere a "
                        f"mitad de rafaga"
                    ),
                )
            )
    return findings
