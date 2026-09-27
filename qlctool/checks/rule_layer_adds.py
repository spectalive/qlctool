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

from .coloured_by_states import coloured_by_states
from .family_frames import family_frame_problems
from .finding import ERROR, Finding
from .fixture_states_colour import fixture_states_colour
from .layer_buttons import layer_buttons
from .show_graph import ShowGraph
from .wrapper_scenes import wrapper_scenes

RULE_ID = "layer_adds"


def check_layer_adds(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element, states: set[int]
) -> list[Finding]:
    if not states:
        return []
    coloured_by_state = coloured_by_states(graph, groups, states)
    findings: list[Finding] = []
    for button in layer_buttons(root, states):
        if family_frame_problems(graph, groups, states, button.widget) == ():
            continue
        scenes = wrapper_scenes(graph, button.function_id)
        if not scenes:
            continue
        clashing = {
            graph.capabilities[fixture_id].fixture.name
            for scene_id in scenes
            for fixture_id, written in graph.driven_of(graph.functions[scene_id], groups).items()
            if fixture_id in coloured_by_state
            and fixture_states_colour(graph.capabilities.get(fixture_id), written)
        }
        if clashing:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(button.function_id),
                    fixtures=tuple(sorted(clashing)),
                    message_id="layer_adds_htp_colour",
                    fields={"caption": button.caption, "count": len(clashing)},
                )
            )
    return findings
