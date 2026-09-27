"""Members of one Collection whose dimmer level a higher concurrent one hides."""

from .dimmer_value_writes import dimmer_value_writes
from .show_graph import ShowGraph


def shadowed_collection_pairs(
    graph: ShowGraph, collection_id: int, reported: set[tuple[int, int, int]]
) -> list[tuple[int, int, int, int, str | None]]:
    """(member, top member, member's low value, top's value, the fixture)."""
    members = graph.members.get(collection_id, ())
    if len(members) < 2:
        return []
    writes = {member: dimmer_value_writes(graph, member) for member in members}

    # channel -> the highest definite value any member writes, and who wrote it.
    highest: dict[tuple[int, int], tuple[int, int]] = {}
    for member, channels in writes.items():
        for channel, values in channels.items():
            value = max(values)
            if channel not in highest or value > highest[channel][0]:
                highest[channel] = (value, member)

    found: list[tuple[int, int, int, int, str | None]] = []
    for member, channels in writes.items():
        for channel, values in channels.items():
            top_value, top_member = highest[channel]
            low = min(values)
            if top_member == member or low >= top_value:
                continue
            key = (collection_id, member, top_member)
            if key in reported:
                continue
            reported.add(key)
            fixture = graph.capabilities.get(channel[0])
            name = fixture.fixture.name if fixture is not None else None
            found.append((member, top_member, low, top_value, name))
    return found
