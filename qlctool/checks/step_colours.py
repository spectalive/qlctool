"""What colour one step of a chaser puts where, over everything the step starts.

The colour rules all begin with the same question - what does this step claim
about colour - and the answer has two sources that look nothing alike in the
file: a Scene writes red, green and blue on named fixtures, and an RGBMatrix
paints one colour across the heads of a fixture group. A signature is the
union of both, hashable so two steps can be compared: two steps with different
signatures are a chaser that rotates colour.
"""

from .matrix_colours import matrix_colours
from .scene_colours import scene_colours
from .show_graph import ShowGraph

# One step's colour claim: hashable items a signature is made of.
Signature = frozenset[tuple[object, ...]]


def step_colours(graph: ShowGraph, groups: dict[int, tuple[int, ...]], step_id: int) -> Signature:
    items: set[tuple[object, ...]] = set()
    for member in graph.descendants(step_id):
        function = graph.functions.get(member)
        if function is None:
            continue
        kind = function.attrib.get("Type")
        if kind in ("Scene", "Sequence"):
            items |= scene_colours(graph, function)
        elif kind == "RGBMatrix":
            items |= matrix_colours(graph, groups, function)
    return frozenset(items)
