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

from .finding import ERROR, Finding
from .short_of_the_endpoint import short_of_the_endpoint
from .show_graph import ShowGraph

RULE_ID = "shutter_endpoint"


def check_shutter_endpoint(graph: ShowGraph, groups: dict[int, tuple[int, ...]]) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        short = short_of_the_endpoint(graph, groups, function_id)
        if not short:
            continue
        names = tuple(sorted(name for name, _, _ in short))
        _, value, endpoint = short[0]
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=graph.name(function_id),
                message_id="shutter_endpoint_half_open",
                fields={"value": value, "endpoint": endpoint},
                fixtures=names,
            )
        )
    return findings
