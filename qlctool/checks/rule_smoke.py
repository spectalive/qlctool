"""A smoke machine caught in somebody else's scene runs until the tank is empty.

The pump has no "off" of its own: it fogs while its channel is up. So a scene
that sweeps every dimmer to full - the natural way to write "everything on" -
turns the machine on and leaves it there for as long as the scene runs, which
unattended means all night.

The rule needs no list of names. A function that fires the pump *and drives
something else* is a function that swept it up by accident; a real smoke scene
fires the pump and nothing but. The pump, not the fixture: a lit fog machine's
LED belongs to the colour bed like any PAR, and a colour scene writing that LED
has not touched the fog.
"""

from .finding import ERROR, Finding
from .fixture_id_is_smoke import fixture_id_is_smoke
from .pump_lit import pump_lit
from .show_graph import ShowGraph

RULE_ID = "smoke"


def check_smoke(graph: ShowGraph, groups: dict[int, tuple[int, ...]]) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        driven = graph.driven_of(function, groups)
        smoke = [
            fixture_id
            for fixture_id, written in driven.items()
            if pump_lit(graph, fixture_id, written)
        ]
        if not smoke:
            continue
        others = [fixture_id for fixture_id in driven if not fixture_id_is_smoke(graph, fixture_id)]
        if others:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message_id="smoke_in_scene",
                    fixtures=tuple(
                        graph.capabilities[fixture_id].fixture.name
                        for fixture_id in smoke
                        if fixture_id in graph.capabilities
                    ),
                )
            )
    return findings
