"""Which leaves of a function a chaser steps into being - and so re-starts.

A leaf that is a *member* of a Collection starts once and runs for the whole
state. A leaf that is a *step* of a Chaser is started anew every time the
chaser reaches it, and a function started later gets a later fader
(`Universe::requestFader` appends after every fader of its priority), which
wins every LTP channel it writes. That is the difference between a layer that
holds under a state and one the state overwrites at its next step.
"""

from .collect_stepped_leaves import collect_stepped_leaves
from .show_graph import ShowGraph


def stepped_leaves(graph: ShowGraph, function_id: int) -> set[int]:
    """Leaf function ids reached through at least one Chaser step."""
    found: set[int] = set()
    collect_stepped_leaves(graph, function_id, False, set(), found)
    return found
