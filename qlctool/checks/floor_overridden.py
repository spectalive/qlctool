"""Whether a floor's aim on a head is written over by a later sibling.

A floor (`static_floors`) is the first member of a room state and holds its LTP
channels only while nothing listed after it writes them. So its aim on a head
counts for nothing while a later member that still runs places that head: the
later member's value is the one on the wire. A home scene parking the washes
at mid-travel is not rescued by the floor under it (2026-09-27).
"""

from .. import roles
from .released_reach import released_reach
from .show_graph import ShowGraph


def floor_overridden(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    later: tuple[int, ...],
    fixture_id: int,
    stopped: frozenset[int],
) -> bool:
    """True when some running member of `later` writes the head's pan or tilt."""
    capability = graph.capabilities.get(fixture_id)
    if capability is None:
        return False
    offsets = {
        *capability.offsets_for_role(roles.PAN),
        *capability.offsets_for_role(roles.TILT),
    }
    return any(
        offsets & set(released_reach(graph, groups, member, stopped).get(fixture_id, {}))
        for member in later
    )
