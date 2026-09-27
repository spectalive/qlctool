"""Whether this driven fixture is a smoke machine with its pump raised."""

from collections.abc import Mapping

from ..fog_offsets import fog_offsets
from .show_graph import ShowGraph, lit


def pump_lit(graph: ShowGraph, fixture_id: int, written: Mapping[int, int | None]) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None or not capability.is_smoke:
        return False
    pump = set(fog_offsets(capability))
    return any(lit(value) for offset, value in written.items() if offset in pump)
