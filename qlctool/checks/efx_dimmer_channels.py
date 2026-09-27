"""(fixture, offset) dimmer channels an EFX under this branch drives."""

from .. import roles
from .show_graph import ShowGraph


def efx_dimmer_channels(graph: ShowGraph, function_id: int) -> set[tuple[int, int]]:
    channels: set[tuple[int, int]] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or function.attrib.get("Type") != "EFX":
            continue
        for fixture_id, pairs in graph.driven_of(function, {}).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or capability.is_smoke:
                continue
            dimmers = set(capability.offsets_for_role(roles.DIMMER))
            channels |= {(fixture_id, offset) for offset in pairs if offset in dimmers}
    return channels
