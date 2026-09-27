"""Whether a set of driven channels includes a fixture's pan or tilt."""

from collections.abc import Mapping

from .. import roles
from .show_graph import ShowGraph


def writes_pan_or_tilt(graph: ShowGraph, fixture_id: int, pairs: Mapping[int, int | None]) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None:
        return False
    return any(
        offset in pairs
        for role in (roles.PAN, roles.TILT)
        for offset in capability.offsets_for_role(role)
    )
