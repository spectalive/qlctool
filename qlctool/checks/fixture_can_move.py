"""Whether a fixture has both a pan and a tilt channel."""

from .. import roles
from .show_graph import ShowGraph


def fixture_can_move(graph: ShowGraph, fixture_id: int) -> bool:
    capability = graph.capabilities.get(fixture_id)
    return (
        capability is not None
        and capability.has_role(roles.PAN)
        and capability.has_role(roles.TILT)
    )
