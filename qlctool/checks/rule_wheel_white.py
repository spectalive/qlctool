"""White on a step of an automatic colour rotation.

"Las luces blancas en las ruedas de colores automáticas no: en teoría es un
color, pero en directo se ve todo iluminado y queda horrible. Luz blanca solo
para blanco total" (owner, 2026-09-22). On paper white is the eighteenth
colour of the palette, and every wheel had it: the rig-wide one, the simple
one, the pastel one (whose white is white), the per-group wheels, the mix
wheels with their "Rojo / Blanco" pairs, the four-colour deal. In the room a
white step is the house lights coming up for three seconds in the middle of
the party, on the wheel's own clock, with nobody having asked for it.

White belongs to the looks somebody presses for it - `Blanco Total`, the
flashes, the talk light - and to nothing that rotates by itself. The rule is
about shape, never about names: every chaser that is a colour clock and is
reachable from a button, whatever it is called, and every step of it. A
fixture is white when its scene puts red, green and blue at one equal, lit
value (which is how `rgbw_split` writes the full white, white emitter and
all), when its colour wheel sits on a detent whose name is white, or when a
matrix paints its group pure white.
"""

from .colour_clocks_below import colour_clocks_below
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .white_fixtures import white_fixtures

RULE_ID = "wheel_white"


def check_wheel_white(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    findings: list[Finding] = []
    judged: dict[int, str] = {}
    for function_id, caption in sorted(entries.items()):
        for chaser_id in sorted(colour_clocks_below(graph, groups, function_id)):
            judged.setdefault(chaser_id, caption)
    for chaser_id, caption in sorted(judged.items()):
        for step_id in graph.members.get(chaser_id, ()):
            white = white_fixtures(graph, groups, step_id)
            if not white:
                continue
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(chaser_id),
                    fixtures=tuple(sorted(white)),
                    message=(
                        f"el paso «{graph.name(step_id)}» pone luz blanca en "
                        f"{len(white)} aparatos por su cuenta, en el reloj de la "
                        "rueda: en directo es la sala encendida; el blanco es de "
                        f"Blanco Total y de nada que gire solo (boton: {caption})"
                    ),
                )
            )
    return findings
