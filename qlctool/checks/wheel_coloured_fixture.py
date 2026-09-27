"""Whether a fixture's colour is a wheel: has a colour macro, but no red."""

from .. import roles
from .show_graph import ShowGraph


def wheel_coloured_fixture(graph: ShowGraph, fixture_id: int) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None:
        return False
    return capability.has_role(roles.COLOR_MACRO) and not capability.has_role(roles.RED)
