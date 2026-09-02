"""A latched layer that writes a channel no state ever puts back.

Every channel outside the Intensity group is LTP: it keeps the last value
written until somebody writes another (`Universe::processFaders` zeroes only
the Intensity ranges). A Toggle button's scene writes while it runs; pressing
it off takes its fader away and writes nothing back, because nothing in QLC+
remembers what was there before. So if *no room state* ever writes that
channel, the button's value is the channel's value for the rest of the night.

That is what the `MultiColor BEAM` buttons did to the four 7R: their
half-colour channel went to 255, no state, no bank and no work light ever
wrote it, and from that press on every colour the wheel picked came out split
in two (cross-audit, 2026-09-02) - the "media luna" the owner had watched on
2026-08-29 has this as one of its causes. A zero is exempt: it is the value
the channel boots with, so leaving it there changes nothing.

`acento sin dueño` asks the same question of Flash buttons, per instant. This
one asks it of Toggles, over every state at once, because a latched layer may
be released under any of them.
"""

from lxml import etree

from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .layer_buttons import layer_buttons
from .show_graph import ShowGraph, reach

RULE = "capa que deja huella"
INTENSITY_GROUP = "Intensity"


def check_layer_trace(
    graph: ShowGraph, groups, root: etree._Element, states: set[int]
) -> list[Finding]:
    if not states:
        return []
    owned = _written_by_states(graph, groups, states)
    findings: list[Finding] = []
    for button in layer_buttons(root, states):
        scene = graph.functions.get(button.function_id)
        if scene is None or scene.attrib.get("Type") != "Scene":
            continue
        stranded: list[str] = []
        for fixture_id, written in driven_channels(scene, graph.capabilities, groups).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            for offset, value in written.items():
                if capability.groups_by_offset[offset] == INTENSITY_GROUP:
                    continue
                if value == 0 or (fixture_id, offset) in owned:
                    continue
                stranded.append(f"{capability.fixture.name} ch{offset + 1}")
        if not stranded:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(button.function_id),
                fixtures=tuple(sorted(set(stranded))),
                message=(
                    f"es un Toggle («{button.caption}») que escribe {len(stranded)} "
                    f"canales LTP que ningun estado de la sala escribe nunca: al "
                    f"apagarlo el valor se queda hasta que alguien lo cambie a mano"
                ),
            )
        )
    return findings


def _written_by_states(graph: ShowGraph, groups, states: set[int]) -> set[tuple[int, int]]:
    owned: set[tuple[int, int]] = set()
    for state_id in states:
        for fixture_id, written in reach(graph, groups, state_id).items():
            owned.update((fixture_id, offset) for offset in written)
    return owned
