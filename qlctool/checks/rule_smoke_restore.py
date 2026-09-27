"""A smoke button whose pump does not fall back to zero on its own.

QLC+ rebuilds its universe from the running faders every cycle, but it only
*resets* the channels in the **Intensity** group before doing so
(`Universe::processFaders` -> `zeroIntensityChannels`, engine/src/universe.cpp).
Every other group keeps whatever was last written. So a Flash over a channel
outside that group is not momentary at all: the release removes the flash's own
fader and the value simply stays.

That is what the four vertical fog machines did. Their Fog channel was declared
in the Effect group, `Humo Vertical YA` raised it while held, and letting go
changed nothing: "le doy y no para de echar todo el rato ... se supone que solo
debe tirar cuando le de" (owner, live, 2026-08-29). The pump is an output level
from 0 to 100%; it belongs in Intensity, and in Intensity the release costs one
DMX frame.

So a smoke button is safe when either is true: the pump channel is one QLC+
resets by itself, or the thing the button starts **carries its own off** - a
haze chaser alternating a fog step with an off step, or a SingleShot burst
whose last step writes the zero. Anything else is a tank waiting to empty into
a room, which is why this is an error and not a warning.
"""

from lxml import etree

from ..vc.build_button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .clears_itself import clears_itself
from .finding import ERROR, Finding
from .pumps_held import pumps_held
from .show_graph import ShowGraph

RULE_ID = "smoke_restore"


def check_smoke_restore(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    findings: list[Finding] = []
    for button in iter_local(console, "Button"):
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id not in graph.functions:
            continue
        held = pumps_held(graph, groups, function_id)
        if not held or clears_itself(graph, groups, function_id, held):
            continue
        caption = button.attrib.get("Caption", "")
        for fixture_id in sorted(held):
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message_id="smoke_restore_pump_left",
                    fields={"caption": caption},
                    fixtures=(graph.capabilities[fixture_id].fixture.name,),
                )
            )
    return findings
