"""Whether a chaser steps through levels: Collections that start other programmes.

An energy cycle is a Chaser whose steps are level Collections, each starting
chasers or collections of its own. It coordinates the room even when the only
family it writes directly is one - the small club's cycle moves only the heads
(2026-09-25) - so the family-owner rules must look through it, not at it.
"""

from .show_graph import ShowGraph


def steps_are_levels(graph: ShowGraph, function_id: int) -> bool:
    """True when every step is a Collection containing a Chaser, Collection or Sequence."""
    members = graph.members.get(function_id, ())
    return bool(members) and all(
        graph.kind(member) == "Collection"
        and any(
            graph.kind(inner) in ("Chaser", "Collection", "Sequence")
            for inner in graph.members.get(member, ())
        )
        for member in members
    )
