"""Two colour clocks ticking in one room state.

The owner saw it in the preview before any rule did: "las barras led van con
los colores a su bola, no siguen el show" (2026-08-26). The rig-wide wheel was
stepping the room through cyan while the bars' own matrix cycle was stepping
the bars through magenta, and both were correct alone. Two chasers that each
rotate colour never agree, because nothing in QLC+ ties one chaser's step to
another's: the room reads as one show and a stray group doing a different one.

A *colour clock* is recognised by shape, never by name: a chaser at least two
of whose steps state different colours on RGB-capable fixtures - through the
scenes they reach, or through the colour an RGBMatrix paints its group. A
room *state* - AUTO, a moment - answers for the whole rig at once, so it gets
one clock at most. A manual layer is not judged here: pressing two colour
layers together is an operator's choice, a state is a promise.
"""

from .colour_clocks_below import colour_clocks_below
from .finding import ERROR, Finding
from .joined import Joined
from .phrase import Phrase
from .show_graph import ShowGraph
from .stray_clock_fixtures import stray_clock_fixtures

RULE_ID = "colour_clocks"


def check_colour_clocks(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    entries: dict[int, str],
    states: set[int] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(states or ()):
        if function_id not in entries:
            continue
        for collection_id in sorted(graph.collections(function_id)):
            clocks: dict[int, set[int]] = {}
            for member in graph.members.get(collection_id, ()):
                found = colour_clocks_below(graph, groups, member)
                if found:
                    clocks[member] = found
            distinct = set().union(*clocks.values()) if clocks else set()
            if len(clocks) < 2 or len(distinct) < 2:
                continue
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(collection_id),
                    message_id="colour_clocks_together",
                    fields={
                        "clocks": Joined(
                            tuple(f"«{graph.name(clock)}»" for clock in sorted(distinct)),
                            Phrase("list_and"),
                        ),
                        "button": entries[function_id],
                    },
                    fixtures=stray_clock_fixtures(graph, groups, distinct),
                )
            )
    return findings
