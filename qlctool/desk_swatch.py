"""The colours a desk tile shows for a look, read from what its scenes write.

A button's background colour on the Mac is decoration and is wrong for most
two-colour looks; the light itself is in the scene values. For every fixture
with red, green and blue channels that the function's scenes reach, the
triple written, with a White emitter's share folded back in, is one colour
of the look; the distinct triples, in fixture order, are its swatches. Smoke machines are not read. A look made only of effects and matrices has none,
and the desk draws none rather than guessing.
"""

from . import roles
from .checks.show_graph import ShowGraph, reach

MAX_SWATCHES = 4
FULL = 255


def swatches(graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int) -> list[str]:
    driven = reach(graph, groups, function_id, kinds=("Scene",))
    found: list[str] = []
    for fixture_id in sorted(driven):
        capability = graph.capabilities.get(fixture_id)
        # A lit smoke machine follows the colour bed or goes white on a flash:
        # it never adds a colour the tile needs, and on FLASH COLOR it would
        # paint the running-colour flash white (round D review, 2026-09-26).
        if capability is None or capability.is_smoke:
            continue
        written = driven[fixture_id]
        triple: list[int] = []
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
        # A White emitter carries the tint's white share (`rgbw_split`): fold it
        # back, or a pastel's tile shows its remainder beside the whole pastel.
        whites = capability.offsets_for_role(roles.WHITE)
        white = (written.get(whites[0]) or 0) if whites else 0
        red, green, blue = (min(FULL, level + white) for level in triple)
        colour = f"#{red:02x}{green:02x}{blue:02x}"
        if colour not in found:
            found.append(colour)
        if len(found) == MAX_SWATCHES:
            break
    return found
