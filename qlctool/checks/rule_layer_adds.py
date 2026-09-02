"""A latched colour layer on top of a state: the colours add, they never replace.

Red, green and blue are Intensity channels and QLC+ mixes those HTP - the
higher write wins, per channel (`Universe::write`). So a Toggle button that
states a colour over a running state does not paint that colour: `AUTO` on
`Rig Cyan` (0,255,255) plus the `Rojo` bank (255,0,0) is 255,255,255 on every
RGB fixture in the group - white, on twenty-seven fixtures in the split patch
(cross-audit, 2026-09-02). It is the same physics as the two energy levels that
turned the room white on 2026-08-25, one floor down, and every colour bank on
the manual page had it.

A colour layer that means to *replace* is a Flash with `ForceLTP`: the scene's
HTP channels are written LTP (`Scene::writeDMX` -> `universe->write(...,
forceLTP=true)` skips the compare) with the Flashing priority that puts its
fader last, so red over cyan is red while the key is down and cyan again when
it lifts. That is what the banks are now. A chaser or a matrix cannot be
flashed, so the per-group wheels, the mixes and the matrix library keep adding
and say so on their frame; this rule is about Scenes, the only kind of layer
that has a fix.
"""

from lxml import etree

from .. import roles
from .color_roles import COLOUR
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .layer_buttons import layer_buttons
from .show_graph import ShowGraph, lit, reach

RULE = "capa que se suma al estado"


def check_layer_adds(
    graph: ShowGraph, groups, root: etree._Element, states: set[int]
) -> list[Finding]:
    if not states:
        return []
    coloured_by_state = _coloured_by_states(graph, groups, states)
    findings: list[Finding] = []
    for button in layer_buttons(root, states):
        scene = graph.functions.get(button.function_id)
        if scene is None or scene.attrib.get("Type") != "Scene":
            continue
        clashing = sorted(
            graph.capabilities[fixture_id].fixture.name
            for fixture_id, written in driven_channels(scene, graph.capabilities, groups).items()
            if fixture_id in coloured_by_state
            and _states_colour(graph.capabilities.get(fixture_id), written)
        )
        if not clashing:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(button.function_id),
                fixtures=tuple(clashing),
                message=(
                    f"es un Toggle («{button.caption}») que pone color sobre "
                    f"{len(clashing)} aparatos que el estado ya colorea: RGB mezcla "
                    f"HTP, asi que rojo sobre cyan es blanco, nunca rojo - un color "
                    f"que sustituye es un Flash con ForceLTP"
                ),
            )
        )
    return findings


def _coloured_by_states(graph: ShowGraph, groups, states: set[int]) -> set[int]:
    coloured: set[int] = set()
    for state_id in states:
        for fixture_id, written in reach(graph, groups, state_id).items():
            if _states_colour(graph.capabilities.get(fixture_id), written):
                coloured.add(fixture_id)
    return coloured


def _states_colour(capability, written: dict[int, int | None]) -> bool:
    if capability is None or capability.is_smoke and not capability.is_lit_smoke:
        return False
    offsets = {offset for role in COLOUR for offset in capability.offsets_for_role(role)}
    wheel = capability.wheel_for_role(roles.COLOR_MACRO)
    if wheel is not None:
        offsets.add(wheel[0])
    return any(lit(written[offset]) for offset in offsets if offset in written)
