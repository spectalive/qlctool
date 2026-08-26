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
off, the same way it carries the shutter open, and this is the check that says
so.
"""

from ..internal_program import internal_program
from .color_roles import COLOUR
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit

RULE = "programa interno"
STATES_COLOUR = ("Scene", "Sequence")


def check_internal_programs(graph: ShowGraph, groups, entries) -> list[Finding]:
    del entries
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        if function.attrib.get("Type") not in STATES_COLOUR:
            continue
        driven = driven_channels(function, graph.capabilities, groups)
        stranded = sorted({
            graph.capabilities[fixture_id].fixture.name
            for fixture_id, written in driven.items()
            if _left_animating(graph, fixture_id, written)
        })
        if stranded:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                message=(
                    "da color a un fixture sin sacarlo de su programa interno: "
                    "mientras ese canal siga en automatico el fixture ignora el "
                    "rojo, verde y azul que le mandas"
                ),
                fixtures=tuple(stranded),
            ))
    return findings


def _left_animating(graph: ShowGraph, fixture_id: int, written) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None or capability.is_smoke:
        return False
    program = internal_program(capability)
    if program is None:
        return False

    coloured = {
        offset for role in COLOUR for offset in capability.offsets_for_role(role)
    }
    if not any(lit(written[o]) for o in coloured if o in written):
        return False
    return written.get(program.mode_offset) != program.off_value
