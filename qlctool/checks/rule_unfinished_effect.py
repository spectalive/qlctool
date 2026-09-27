"""An animation the chaser cuts off before it has finished.

An RGBMatrix does not run "for a while": it walks a fixed number of frames and
starts again, and how many depends on the script *and* on the grid it paints.
Fill on an eight-wide bar is eight frames; Waves on the same bar is twelve. A
chaser holding such a matrix for less than that stops it wherever it had got
to, which on Fill means the bar lights half way, jumps to another colour, and
lights half way again, all night.

The owner found it before this check did: "la barra led empezamos con una
animacion pero nunca la terminamos" (2026-08-26). It is also half of why the
pixels read as off - an animation cut in its first half is an animation seen
mostly dark.

A function on **Beats** tempo is skipped: its numbers are thousandths of a
beat, not milliseconds, and how long a beat lasts is the room's business.
"""

from .cut_matrix_steps import cut_matrix_steps
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .tempo_element_is_beats import tempo_element_is_beats

RULE_ID = "unfinished_effect"


def check_unfinished_effects(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    del groups, entries
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        if function.attrib.get("Type") != "Chaser" or tempo_element_is_beats(function):
            continue
        cut = cut_matrix_steps(graph, function)
        if not cut:
            continue
        worst = max(cut, key=lambda item: item[2] - item[1])
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=graph.name(function_id),
                message_id="unfinished_effect_cut",
                fields={
                    "count": len(cut),
                    "effect": worst[0],
                    "needed": worst[2],
                    "given": worst[1],
                },
            )
        )
    return findings
