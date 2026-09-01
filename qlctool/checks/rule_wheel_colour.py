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

from .. import roles
from .color_roles import COLOUR
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit, reach

RULE = "rueda de color"
STATES_COLOUR = ("Scene", "Sequence")


def check_wheel_colour(graph: ShowGraph, groups, entries: dict[int, str]) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, caption in sorted(entries.items()):
        stated = reach(graph, groups, function_id, kinds=STATES_COLOUR)
        everything = reach(graph, groups, function_id)
        missed: set[str] = set()
        for members in groups.values():
            if not _colours_any(graph, stated, members):
                continue
            missed |= {
                graph.capabilities[fixture_id].fixture.name
                for fixture_id in members
                if _is_wheel_coloured(graph, fixture_id) and not everything.get(fixture_id)
            }
        if missed:
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        "da color a un grupo pero no escribe nada en los fixtures "
                        "de ese grupo cuyo color es una rueda: se quedan con el "
                        f"color anterior (boton: {caption})"
                    ),
                    fixtures=tuple(sorted(missed)),
                )
            )
    return findings


def _is_wheel_coloured(graph: ShowGraph, fixture_id: int) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None or capability.is_smoke:
        return False
    if any(capability.has_role(r) for r in (roles.RED, roles.GREEN, roles.BLUE)):
        return False
    return capability.wheel_for_role(roles.COLOR_MACRO) is not None


def _colours_any(graph: ShowGraph, stated, members) -> bool:
    for fixture_id in members:
        capability = graph.capabilities.get(fixture_id)
        written = stated.get(fixture_id)
        if capability is None or not written:
            continue
        offsets = {o for role in COLOUR for o in capability.offsets_for_role(role)}
        if any(lit(written[o]) for o in offsets if o in written):
            return True
    return False
