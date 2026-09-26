"""A tint whose white share went to fixtures that have no White emitter.

`rule_white_twice` made the split right on the fixtures with a white LED:
the achromatic part of a tint leaves red, green and blue and goes to White.
The generator then wrote the same reduced RGB to every fixture of the scene,
White or not. On the twenty-three without one, `Rig Pastel Rojo` - "mezclado
un 55 % hacia el blanco" - came out a dim saturated red (115, 0, 0), and the
talk light a brown (85, 44, 0) instead of warm white (en-sala DMX audit,
2026-09-26, items 1 and 9).

The rule reads values and capabilities, never a name (`dropped_white_share`):
in one Scene, and in one step of a chaser across the scenes that step starts,
a fixture with RGB and no White role written exactly the RGB a White-emitter
fixture carries beside a lit White is a fixture that got the remainder of the
split and lost the rest of the colour. A step is reported only for fixtures
none of its own scenes already reports.
"""

from .dropped_white_share import dropped_white_share
from .finding import ERROR, Finding
from .fixture_names_of import fixture_names_of
from .show_graph import ShowGraph

RULE_ID = "white_share_dropped"
STEP_KINDS = ("Scene", "Sequence")


def check_white_share_dropped(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]]
) -> list[Finding]:
    findings: list[Finding] = []
    by_scene: dict[int, set[int]] = {}
    for function_id, function in sorted(graph.functions.items()):
        if function.attrib.get("Type") != "Scene":
            continue
        dropped = dropped_white_share(graph, [graph.driven_of(function, groups)])
        by_scene[function_id] = dropped
        if dropped:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    fixtures=fixture_names_of(graph, dropped),
                    message_id="white_share_dropped_scene",
                    fields={"count": len(dropped)},
                )
            )
    judged: set[int] = set()
    for chaser_id in sorted(graph.members):
        if graph.kind(chaser_id) != "Chaser":
            continue
        for step_id in graph.members[chaser_id]:
            if step_id in judged or graph.kind(step_id) in STEP_KINDS:
                continue
            judged.add(step_id)
            scenes = [m for m in graph.descendants(step_id) if graph.kind(m) in STEP_KINDS]
            if len(scenes) < 2:
                continue
            dropped = dropped_white_share(
                graph, [graph.driven(scene, {}) for scene in sorted(scenes)]
            )
            dropped -= set().union(*(by_scene.get(scene, set()) for scene in scenes))
            if dropped:
                findings.append(
                    Finding(
                        rule_id=RULE_ID,
                        severity=ERROR,
                        function=graph.name(chaser_id),
                        fixtures=fixture_names_of(graph, dropped),
                        message_id="white_share_dropped_step",
                        fields={"step": graph.name(step_id), "count": len(dropped)},
                    )
                )
    return findings
