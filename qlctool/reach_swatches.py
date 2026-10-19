"""The colours one function's scenes state together, read from its merged reach.

Right for a look whose scenes all run at once - a Scene, or a Collection of
them. A Chaser's steps never run together, so `swatches` reads each step on
its own instead of asking this of the chaser.
"""

from .checks.fixture_colour import fixture_colour
from .checks.reach import reach
from .checks.show_graph import ShowGraph
from .max_swatches import MAX_SWATCHES


def reach_swatches(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> list[str]:
    driven = reach(graph, groups, function_id, kinds=("Scene",))
    found: list[str] = []
    for fixture_id in sorted(driven):
        capability = graph.capabilities.get(fixture_id)
        # A lit smoke machine follows the colour bed or goes white on a flash:
        # it never adds a colour the tile needs, and on FLASH COLOR it would
        # paint the running-colour flash white (round D review, 2026-09-26).
        if capability is None or capability.is_smoke:
            continue
        # A White emitter carries the tint's white share (`rgbw_split`):
        # `fixture_colour` folds it back, or a pastel's tile shows its
        # remainder beside the whole pastel.
        stated = fixture_colour(graph, fixture_id, driven[fixture_id])
        if stated is None:
            continue
        red, green, blue = stated
        colour = f"#{red:02x}{green:02x}{blue:02x}"
        if colour not in found:
            found.append(colour)
        if len(found) == MAX_SWATCHES:
            break
    return found
