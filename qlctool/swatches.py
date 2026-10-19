"""The colours a desk tile shows for a look, read from what its scenes write.

A button's background colour on the Mac is decoration and is wrong for most
two-colour looks; the light itself is in the scene values. For every fixture
with red, green and blue channels that the function's scenes reach, the
triple written, with a White emitter's share folded back in, is one colour
of the look; the distinct triples, in fixture order, are its swatches. Smoke machines are not read. A look made only of effects and matrices has none,
and the desk draws none rather than guessing.

A Chaser's steps are alternatives, never concurrent, so its tile shows the
colours of each step in step order, deduplicated (`chaser_swatches`): the
merged reach takes the highest value of every channel across all the steps,
which is a colour the wheel never shows (`Pastel tenue` read #ffffff,
en-sala round 1, 2026-09-26).
"""

from .chaser_swatches import chaser_swatches
from .checks.show_graph import ShowGraph
from .reach_swatches import reach_swatches


def swatches(graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int) -> list[str]:
    if graph.kind(function_id) == "Chaser":
        return chaser_swatches(graph, groups, function_id)
    return reach_swatches(graph, groups, function_id)
