"""A strobe chaser whose black half is made of channels a lit state out-bids.

`Strobo Rapido` and `Strobo Medio` were chasers alternating a white scene and a
black one. Every channel the black scene wrote - dimmers, red, green, blue - is
in the Intensity group, and Intensity is HTP: with a room state holding those
dimmers at 255, the zeros lost the compare (`Universe::write`, the lower value
is dropped) and the "black" step changed nothing at all. Under AUTO the room
saw white / state-colour, never white / black, and the four BEAM 7R had their
colour wheel commanded white and back every 125 ms (cross-audit, 2026-09-02).
The strobe only did what its button said under `Todo Negro`.

A chaser cannot blink a fixture to black on top of a lit state unless its
dark step owns something that is *not* HTP - a shutter, driven closed or
strobing - so the rule reads the shape: a chaser with a strobe's shape whose
dark steps write only Intensity-group channels, reachable from a layer button
(a button that is not itself the room's state), is a strobe that cannot go
dark. The honest strobe on a lit room is a held scene on the shutters.
"""

from lxml import etree

from .. import roles
from .finding import ERROR, Finding
from .layer_buttons import layer_buttons
from .show_graph import ShowGraph, lit, reach
from .strobe_shape import strobe_flash_rate

RULE = "estrobo sin negro"
INTENSITY_GROUP = "Intensity"


def check_strobe_black(
    graph: ShowGraph, groups, root: etree._Element, states: set[int]
) -> list[Finding]:
    findings: list[Finding] = []
    reported: set[int] = set()
    for button in layer_buttons(root, states):
        for function_id in sorted(graph.descendants(button.function_id)):
            if function_id in reported:
                continue
            function = graph.functions.get(function_id)
            if function is None or function.attrib.get("Type") != "Chaser":
                continue
            if strobe_flash_rate(graph, groups, function_id) is None:
                continue
            dark_steps = [
                step
                for step in graph.members.get(function_id, ())
                if _all_dark_and_htp(graph, groups, step)
            ]
            if not dark_steps:
                continue
            reported.add(function_id)
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        f"cuelga de «{button.caption}» y su paso negro "
                        f"({graph.name(dark_steps[0])}) solo escribe canales "
                        f"Intensity, que mezclan HTP: con un estado encendido "
                        f"debajo el 0 pierde y el estrobo nunca llega a negro - "
                        f"un estrobo sobre la sala es una escena mantenida en "
                        f"los shutters"
                    ),
                )
            )
    return findings


def _all_dark_and_htp(graph: ShowGraph, groups, step_id: int) -> bool:
    """A step whose only claim to darkness is zeros on Intensity channels.

    A shutter or strobe channel written is a way to go dark that HTP cannot
    veto, so a step that drives one is not this shape. Any other LTP channel
    it parks (a panel's mode, say) darkens nothing and is ignored.
    """
    wrote = False
    for fixture_id, written in reach(graph, groups, step_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        for offset, value in written.items():
            if capability.roles_by_offset[offset] == roles.STROBE:
                return False
            if capability.groups_by_offset[offset] != INTENSITY_GROUP:
                continue
            if lit(value):
                return False
            wrote = True
    return wrote
