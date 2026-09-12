"""The colours a desk tile shows for a look, read from what its scenes write.

A button's background colour on the Mac is decoration and is wrong for most
two-colour looks; the light itself is in the scene values. For every fixture
with red, green and blue channels that the function's scenes reach, the
triple written is one colour of the look; the distinct triples, in fixture
order, are its swatches. A look made only of effects and matrices has none,
and the desk draws none rather than guessing.
"""

from . import roles
from .checks.show_graph import ShowGraph, reach

MAX_SWATCHES = 4


def swatches(graph: ShowGraph, groups, function_id: int) -> list[str]:
    driven = reach(graph, groups, function_id, kinds=("Scene",))
    found: list[str] = []
    for fixture_id in sorted(driven):
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        written = driven[fixture_id]
        triple = []
        for role in (roles.RED, roles.GREEN, roles.BLUE):
            offsets = capability.offsets_for_role(role)
            if not offsets:
                triple = []
                break
            value = written.get(offsets[0])
            if value is None:
                triple = []
                break
            triple.append(value)
        if len(triple) != 3:
            continue
        colour = "#%02x%02x%02x" % tuple(triple)
        if colour not in found:
            found.append(colour)
        if len(found) == MAX_SWATCHES:
            break
    return found
