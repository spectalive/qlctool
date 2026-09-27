"""Whether a fixture's colour comes from a wheel rather than RGB channels."""

from .. import roles
from .show_graph import ShowGraph


def is_wheel_coloured(graph: ShowGraph, fixture_id: int) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None or capability.is_smoke:
        return False
    if any(capability.has_role(r) for r in (roles.RED, roles.GREEN, roles.BLUE)):
        return False
    return capability.wheel_for_role(roles.COLOR_MACRO) is not None
