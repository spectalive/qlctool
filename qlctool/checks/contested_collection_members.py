"""Members of one Collection whose contested channels overlap, once each."""

from collections.abc import Collection
from itertools import combinations

from .contested_channels import contested_channels
from .show_graph import ShowGraph
from .static_floors import static_floors


def contested_collection_members(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    collection_id: int,
    reported: set[tuple[int, int, int]],
    states: Collection[int],
) -> list[tuple[int, int, tuple[str, ...]]]:
    """(first member, second member, the fixtures their contested channels share)."""
    members = graph.members.get(collection_id, ())
    if len(members) < 2:
        return []
    contested = {member: contested_channels(graph, groups, member) for member in members}
    floors = static_floors(graph, groups, collection_id, states)
    found: list[tuple[int, int, tuple[str, ...]]] = []
    for first, second in combinations(members, 2):
        if first in floors:
            continue
        shared = contested[first].keys() & contested[second].keys()
        if not shared:
            continue
        key = (collection_id, first, second)
        if key in reported:
            continue
        reported.add(key)
        fixtures = tuple(
            sorted(
                {
                    graph.capabilities[fixture_id].fixture.name
                    for fixture_id, _ in shared
                    if fixture_id in graph.capabilities
                }
            )
        )
        found.append((first, second, fixtures))
    return found
