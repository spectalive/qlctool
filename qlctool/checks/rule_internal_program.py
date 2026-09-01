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

from .. import roles
from ..internal_program import internal_program
from .color_roles import COLOUR
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit, reach

RULE = "programa interno"
STATES_COLOUR = ("Scene", "Sequence")


def check_internal_programs(
    graph: ShowGraph, groups, entries, states: set[int] | None = None
) -> list[Finding]:
    del entries
    owned = _mode_owned_fixtures(graph, groups, states or set())
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        if function.attrib.get("Type") not in STATES_COLOUR:
            continue
        driven = driven_channels(function, graph.capabilities, groups)
        stranded = sorted(
            {
                graph.capabilities[fixture_id].fixture.name
                for fixture_id, written in driven.items()
                if fixture_id not in owned and _left_animating(graph, fixture_id, written)
            }
        )
        if stranded:
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        "da color a un fixture sin sacarlo de su programa interno: "
                        "mientras ese canal siga en automatico el fixture ignora el "
                        "rojo, verde y azul que le mandas"
                    ),
                    fixtures=tuple(stranded),
                )
            )
    return findings


def _mode_owned_fixtures(graph: ShowGraph, groups, states: set[int]) -> set[int]:
    """Fixtures whose mode channel every lighting room state drives.

    Owned means deterministic: whichever state is running, something in it is
    writing the mode channel, so a colour scene's RGB reads or is ignored by
    that state's decision - never by whatever ran before. A state that keeps
    the fixture dark is excused the way `rule_accent_restore` excuses it. No
    states, no owners: the rule then demands the mode-off write in the scene
    itself, exactly as before.
    """
    if not states:
        return set()
    state_reach = [reach(graph, groups, state_id) for state_id in states]
    owned: set[int] = set()
    for fixture_id, capability in graph.capabilities.items():
        program = internal_program(capability)
        if program is None:
            continue
        dimmers = capability.offsets_for_role(roles.DIMMER)
        lighting = [
            driven
            for driven in state_reach
            if any(lit(driven.get(fixture_id, {}).get(offset, 0)) for offset in dimmers)
        ]
        if lighting and all(
            program.mode_offset in driven.get(fixture_id, {}) for driven in lighting
        ):
            owned.add(fixture_id)
    return owned


def _left_animating(graph: ShowGraph, fixture_id: int, written) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None or capability.is_smoke:
        return False
    program = internal_program(capability)
    if program is None:
        return False

    coloured = {offset for role in COLOUR for offset in capability.offsets_for_role(role)}
    if not any(lit(written[o]) for o in coloured if o in written):
        return False
    return written.get(program.mode_offset) != program.off_value
