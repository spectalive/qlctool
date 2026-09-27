"""Members of one Collection where an EFX's dimmer dips are held at 255, once each."""

from .efx_dimmer_channels import efx_dimmer_channels
from .full_dimmer_writes import full_dimmer_writes
from .show_graph import ShowGraph


def masked_collection_pairs(
    graph: ShowGraph, collection_id: int, reported: set[tuple[int, int, int]]
) -> list[tuple[int, int, tuple[str, ...]]]:
    """(efx member, full member, the fixtures the full member masks on it)."""
    members = graph.members.get(collection_id, ())
    if len(members) < 2:
        return []
    efx_channels = {member: efx_dimmer_channels(graph, member) for member in members}
    full_channels = {member: full_dimmer_writes(graph, member) for member in members}

    found: list[tuple[int, int, tuple[str, ...]]] = []
    for efx_member, driven in efx_channels.items():
        for full_member, held in full_channels.items():
            if efx_member == full_member:
                continue
            masked = driven & held
            if not masked:
                continue
            key = (collection_id, efx_member, full_member)
            if key in reported:
                continue
            reported.add(key)
            names = tuple(
                sorted(
                    {
                        graph.capabilities[fixture].fixture.name
                        for fixture, _ in masked
                        if fixture in graph.capabilities
                    }
                )
            )
            found.append((efx_member, full_member, names))
    return found
