"""Cache state_owners across calls for one graph, groups and room states."""

from .show_graph import ShowGraph
from .state_owners import state_owners

_OWNER_CACHE: list[
    tuple[ShowGraph, dict[int, tuple[int, ...]], frozenset[int], dict[str, set[int]]]
] = []


def cached_state_owners(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int]
) -> dict[str, set[int]]:
    state_ids = frozenset(states)
    if _OWNER_CACHE:
        cached_graph, cached_groups, cached_states, owners = _OWNER_CACHE[0]
        if cached_graph is graph and cached_groups is groups and cached_states == state_ids:
            return owners
    owners = state_owners(graph, groups, states)
    _OWNER_CACHE[:] = [(graph, groups, state_ids, owners)]
    return owners
