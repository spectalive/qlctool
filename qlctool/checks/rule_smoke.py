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

from ..fog_offsets import fog_offsets
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit

RULE = "humo"


def check_smoke(graph: ShowGraph, groups, entries) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        driven = driven_channels(function, graph.capabilities, groups)
        smoke = [
            fixture_id
            for fixture_id, written in driven.items()
            if _pump_lit(graph, fixture_id, written)
        ]
        if not smoke:
            continue
        others = [fixture_id for fixture_id in driven if not _is_smoke(graph, fixture_id)]
        if others:
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        "enciende la maquina de humo dentro de una escena que "
                        "toca otros fixtures: el humo se queda abierto mientras "
                        "esa escena corra"
                    ),
                    fixtures=tuple(
                        graph.capabilities[fixture_id].fixture.name
                        for fixture_id in smoke
                        if fixture_id in graph.capabilities
                    ),
                )
            )
    return findings


def _is_smoke(graph: ShowGraph, fixture_id: int) -> bool:
    capability = graph.capabilities.get(fixture_id)
    return capability is not None and capability.is_smoke


def _pump_lit(graph: ShowGraph, fixture_id: int, written) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None or not capability.is_smoke:
        return False
    pump = set(fog_offsets(capability))
    return any(lit(value) for offset, value in written.items() if offset in pump)
