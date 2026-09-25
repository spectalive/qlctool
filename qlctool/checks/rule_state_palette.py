"""More than two colours at once, on a rotation a room state runs by itself.

"Los colores siguen siendo una feria" (owner, 2026-09-22). The wheel AUTO
ran had eighteen solid steps, five contrasts, two steps with every fixture on
a colour of its own and four with the rig dealt into quarters - and Random
order put a wild one on the room every few minutes, whether the moment was a
speech or a slow song. What the owner wants left running unattended is subtle:
one colour, or two at most - red against yellow, yellow against blue - and the
multicolour look kept on a button of its own, "solo por si acaso".

So a room state - AUTO, a moment - promises at most two colours per step of
any colour clock it starts. Counting is by what the eye sees, not by what the
file says: a pastel on a fixture with a white emitter and the same pastel on
one without are one colour (`step_palette` folds the white back in), and a
matrix counts for the colour it paints. A layer somebody presses is not judged
here, which is exactly where the multicolour wheel lives.
"""

from .colour_clocks_below import colour_clocks_below
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .step_palette import step_palette

RULE_ID = "state_palette"
AT_MOST = 2


def check_state_palette(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    entries: dict[int, str],
    states: set[int] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    judged: dict[int, str] = {}
    for function_id in sorted(states or ()):
        if function_id not in entries:
            continue
        for chaser_id in sorted(colour_clocks_below(graph, groups, function_id)):
            judged.setdefault(chaser_id, entries[function_id])
    for chaser_id, caption in sorted(judged.items()):
        for step_id in graph.members.get(chaser_id, ()):
            colours = step_palette(graph, groups, step_id)
            if len(colours) <= AT_MOST:
                continue
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(chaser_id),
                    message_id="state_palette_too_many",
                    fields={"step": graph.name(step_id), "count": len(colours), "button": caption},
                )
            )
    return findings
