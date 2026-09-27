"""Colour with no way out of the fixture: the check for a light that stays dark.

Two of this show's bugs were the same bug wearing different clothes. A matrix
painted the panels beautifully and never touched their master dimmer, so they
were the right colour and off. The beams' gobo scenes opened a dimmer on a
fixture whose mechanical shutter was still shut, so they were aimed and off.

The rule is one sentence: **if a button puts colour on a fixture, something that
same button starts has to open that fixture's intensity path** - its dimmer if
it has one, its shutter if the definition labels one. Anything else is a button
that promises light and does not deliver it.
"""

from .finding import ERROR, Finding
from .intensity_dark_fixtures import intensity_dark_fixtures
from .reach import reach
from .show_graph import ShowGraph

RULE_ID = "intensity"
# A Scene states a colour. A matrix paints one group's pixels and an EFX moves
# a head: those are layers, and a layer answers to the state beneath it.
STATES_COLOUR = ("Scene", "Sequence")


def check_intensity(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    entries: dict[int, str],
    states: set[int] | None = None,
) -> list[Finding]:
    """Every button, judged by what it is responsible for.

    A **state** of the room - AUTO, a moment, the work light - runs with
    nothing underneath it, so it answers for every fixture it colours by any
    means at all, its matrices included. That is the check the panels failed:
    AUTO painted them and nothing opened them.

    Everything else is a **layer**, pressed on top of whatever state is
    running, and answers only for the colour it states itself, in a Scene. A
    matrix on the library page is not asked to open a dimmer, because it is
    incapable of it and the state beneath it already has.
    """
    states = states or set()
    findings: list[Finding] = []
    for function_id, caption in sorted(entries.items()):
        is_state = function_id in states
        kinds = None if is_state else STATES_COLOUR
        dark = intensity_dark_fixtures(
            graph,
            reach(graph, groups, function_id, kinds=kinds),
            layer=not is_state,
        )
        if not dark:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=graph.name(function_id),
                # The catalogue says one fixture and several in two entries.
                message_id="intensity_dark_one" if len(dark) == 1 else "intensity_dark_many",
                fields={"button": caption},
                fixtures=tuple(sorted(dark)),
            )
        )
    return findings
