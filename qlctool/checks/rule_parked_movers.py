"""A block of the automatic show that moves one family and parks the other.

2026-08-29, live: "las 7R ... no se mueven", with nothing pressed but AUTO.
Nothing was broken in the beams. `Nivel Ambiente` - the first and longest step
of `Ciclo Energia` - started the washes' slow shapes and a *static* fan scene
for the beams, so for the level's whole four-minute hold the four 7R held one
position. A needle that never moves does not read as rest; it reads as four
lights that failed.

The rule is about blocks the show runs by itself. A Collection that is a step
of a Chaser is such a block: it starts everything in it at once and holds for
that step. If anything in it moves a head, the block is a movement block, and
every head in the rig has to be moving inside it - a head left out is left out
for the whole step, however long that is.

A Collection somebody presses is not asked the same question: a button named
after one shape is allowed to move only the fixtures that draw that shape, and
the operator can see what they pressed.
"""

from .. import roles
from ..xmlutil import find_local, findall_local
from .driven_channels import EFX_PAN_TILT
from .finding import ERROR, Finding
from .show_graph import CONCURRENT, ShowGraph

RULE = "cabezas paradas en el ciclo"


def check_parked_movers(graph: ShowGraph) -> list[Finding]:
    movers = {
        fixture_id
        for fixture_id, capability in graph.capabilities.items()
        if not capability.is_smoke
        and capability.has_role(roles.PAN)
        and capability.has_role(roles.TILT)
    }
    if len(movers) < 2:
        return []

    findings: list[Finding] = []
    seen: set[int] = set()
    for chaser_id in sorted(graph.functions):
        if graph.kind(chaser_id) != "Chaser":
            continue
        for step in graph.members.get(chaser_id, ()):
            if graph.kind(step) != CONCURRENT or step in seen:
                continue
            seen.add(step)
            moved = _moved_heads(graph, step)
            if not moved:
                continue
            parked = movers - moved
            if not parked:
                continue
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(step),
                    message=(
                        "es un bloque del ciclo automatico que mueve unas cabezas "
                        "y deja estas quietas durante todo el paso: una lira que "
                        "no se mueve durante minutos parece averiada, no en reposo"
                    ),
                    fixtures=tuple(
                        sorted(graph.capabilities[fixture_id].fixture.name for fixture_id in parked)
                    ),
                )
            )
    return findings


def _moved_heads(graph: ShowGraph, function_id: int) -> set[int]:
    """The fixtures an EFX inside this block drives on pan and tilt."""
    moved: set[int] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or function.attrib.get("Type") != "EFX":
            continue
        for element in findall_local(function, "Fixture"):
            identifier = find_local(element, "ID")
            if identifier is None or not (identifier.text or "").strip().isdigit():
                continue
            mode = find_local(element, "Mode")
            mode_value = int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT
            if mode_value != EFX_PAN_TILT:
                continue
            fixture_id = int(identifier.text)
            if fixture_id in graph.capabilities:
                moved.add(fixture_id)
    return moved
