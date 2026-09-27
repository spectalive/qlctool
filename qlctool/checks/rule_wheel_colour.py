"""A look that colours a group and skips the members whose colour is a wheel.

Every generator that reasons in red, green and blue reads a fixture, finds no
red channel, and moves on. On the BEAM 230W 7R - colour on a wheel, no RGB at
all - that is silence, not a decision: `BLANCO TOTAL` left the four of them
black while lighting everything else, and `Rueda Mezcla` walked the whole rig
through thirty pairs of colours with the beams stuck on whatever they had.

The rule needs no threshold. A look that states a colour on a fixture group has
made a claim about that group, and the beams are *in* the Cabezas group; a look
that says "the heads are red" and leaves four of them on last night's magenta
is wrong however many fixtures it got right.

Only what a **Scene** states counts as stating a colour. A matrix paints the
pixels of a group and can say nothing about a fixture that has none, so it is
not asked to.
"""

from .colours_any import colours_any
from .finding import ERROR, Finding
from .is_wheel_coloured import is_wheel_coloured
from .reach import reach
from .show_graph import ShowGraph

RULE_ID = "wheel_colour"
STATES_COLOUR = ("Scene", "Sequence")


def check_wheel_colour(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, caption in sorted(entries.items()):
        stated = reach(graph, groups, function_id, kinds=STATES_COLOUR)
        everything = reach(graph, groups, function_id)
        missed: set[str] = set()
        for members in groups.values():
            if not colours_any(graph, stated, members):
                continue
            missed |= {
                graph.capabilities[fixture_id].fixture.name
                for fixture_id in members
                if is_wheel_coloured(graph, fixture_id) and not everything.get(fixture_id)
            }
        if missed:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message_id="wheel_colour_missed",
                    fields={"button": caption},
                    fixtures=tuple(sorted(missed)),
                )
            )
    return findings
