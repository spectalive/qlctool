"""Whether a chaser rotates colour: at least two steps stating different, non-dark colours."""

from .show_graph import ShowGraph
from .step_colours import Signature, step_colours


def is_colour_clock(graph: ShowGraph, groups: dict[int, tuple[int, ...]], chaser_id: int) -> bool:
    stated: set[Signature] = set()
    for step in graph.members.get(chaser_id, ()):
        signature = step_colours(graph, groups, step)
        if signature:
            stated.add(signature)
        if len(stated) >= 2:
            return True
    return False
