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
from .show_graph import ShowGraph
from .step_colours import step_colours

RULE_ID = "colour_clocks"


def check_colour_clocks(
    graph: ShowGraph, groups, entries: dict[int, str], states: set[int] | None = None
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
                    message=(
                        "arranca a la vez "
                        + " y ".join(f"«{graph.name(clock)}»" for clock in sorted(distinct))
                        + ", dos ciclos que rotan color cada uno a su ritmo: los "
                        f"fixtures de uno van a su bola respecto al resto "
                        f"(boton: {entries[function_id]})"
                    ),
                    fixtures=_stray_fixtures(graph, groups, distinct),
                )
            )
    return findings


def _stray_fixtures(graph: ShowGraph, groups, clock_ids: set[int]) -> tuple[str, ...]:
    """The fixtures the narrower clocks paint: the group off on its own beat."""
    painted = {
        clock: {
            item[0]
            for step in graph.members.get(clock, ())
            for item in step_colours(graph, groups, step)
        }
        for clock in clock_ids
    }
    widest = max(painted, key=lambda clock: len(painted[clock]))
    stray = set().union(*(fixtures for clock, fixtures in painted.items() if clock != widest))
    return tuple(
        sorted(
            graph.capabilities[fixture_id].fixture.name
            for fixture_id in stray
            if fixture_id in graph.capabilities
        )
    )
