"""A look that states a colour on a fixture still running its own programme.

Some fixtures animate themselves. The HYULIGHTS panels have forty-two built-in
effects behind one mode channel, and while that channel is in its automatic
position the fixture **ignores the red, green and blue it is sent**. Nothing
resets the channel on its own, either: it keeps whatever the last look left
there.

So a scene that says "the panels are white" and does not also say "stop
animating" is a scene that does nothing to them - and the way it fails is the
worst kind, because it depends on what ran before. Press it after the colour
bank and it works; press it after AUTO and the panels carry on with last
night's effect through a speech.

Every scene that states a colour therefore carries the mode channel back to
off, the same way it carries the shutter open - unless the mode channel has a
*standing owner*: when every room state that lights the fixture also drives
its mode channel, "what ran before" is no longer a matter of luck but a
deliberate phase (`Ciclo Paneles Mixto` flipping the panels between their own
programmes and manual, while the wheel writes their RGB all night). The bug
this rule was written for is an unowned mode channel; an owned one is the
design working.
"""

from .finding import ERROR, Finding
from .left_animating import left_animating
from .mode_owned_fixtures import mode_owned_fixtures
from .show_graph import ShowGraph

RULE_ID = "internal_program"
STATES_COLOUR = ("Scene", "Sequence")


def check_internal_programs(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    entries: dict[int, str],
    states: set[int] | None = None,
) -> list[Finding]:
    del entries
    owned = mode_owned_fixtures(graph, groups, states or set())
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        if function.attrib.get("Type") not in STATES_COLOUR:
            continue
        driven = graph.driven_of(function, groups)
        stranded = sorted(
            {
                graph.capabilities[fixture_id].fixture.name
                for fixture_id, written in driven.items()
                if fixture_id not in owned and left_animating(graph, fixture_id, written)
            }
        )
        if stranded:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message_id="internal_program_colour",
                    fixtures=tuple(stranded),
                )
            )
    return findings
