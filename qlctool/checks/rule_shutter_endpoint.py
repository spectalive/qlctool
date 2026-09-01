"""A shutter parked inside its open range, but short of the end of it.

2026-08-29, live at the show: every beam scene wrote 248 to the BEAM 230W 7R's
shutter - the middle of the range its manual calls "241-255 Open" - and the
beams stayed black. At 255 they lit. The hand-built show had always sent 255,
and nobody knew why until that night.

So a published range is a promise about its *endpoint*, not about every value
inside it. The heads read a value that ought to be open and keep the shutter
shut, and no amount of dimmer argues with a shut shutter. A generator picking a
"safely inside" value is exactly how a scene ends up correct on paper and dark
in the room.

The rule: a function that writes a fixture's shutter into its open range has to
write the endpoint of that range (`shutter_open_value`: the top of the channel
when the range reaches 255, the bottom when it starts at 0). Values outside the
open range - closed, or a labelled strobing range - are somebody's deliberate
choice and are left alone; only a value that *means* open without reaching the
endpoint is reported.
"""

from ..shutter_open import shutter_open_ranges
from ..shutter_open_value import shutter_open_value
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "obturador a medio abrir"


def check_shutter_endpoint(graph: ShowGraph, groups) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        short = _short_of_the_endpoint(graph, groups, function_id)
        if not short:
            continue
        names = tuple(sorted(name for name, _, _ in short))
        _, value, endpoint = short[0]
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                message=(
                    f"abre el obturador a {value} en vez de {endpoint}: dentro del "
                    f"rango 'abierto', pero sin llegar al extremo - la 7R se queda "
                    f"a oscuras en mitad de ese rango"
                ),
                fixtures=names,
            )
        )
    return findings


def _short_of_the_endpoint(
    graph: ShowGraph, groups, function_id: int
) -> list[tuple[str, int, int]]:
    """(fixture name, value written, the endpoint it should have written)."""
    driven = driven_channels(graph.functions[function_id], graph.capabilities, groups)
    short: list[tuple[str, int, int]] = []
    for fixture_id, written in driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        for offset, opening in shutter_open_ranges(capability):
            value = written.get(offset)
            if value is None:
                continue
            endpoint = shutter_open_value(opening)
            if opening.minimum <= value <= opening.maximum and value != endpoint:
                short.append((capability.fixture.name, value, endpoint))
    return short
