"""The fixtures whose dimmer a chaser's steps put at different levels."""

from .. import roles
from .show_graph import ShowGraph


def pulsed_dimmer_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], chaser_id: int
) -> set[str]:
    levels: dict[int, set[int | None]] = {}
    for step in graph.members.get(chaser_id, ()):
        for leaf in graph.descendants(step):
            function = graph.functions.get(leaf)
            if function is None:
                continue
            for fixture_id, pairs in graph.driven_of(function, groups).items():
                capability = graph.capabilities.get(fixture_id)
                if capability is None:
                    continue
                for offset in capability.offsets_for_role(roles.DIMMER):
                    if offset in pairs:
                        levels.setdefault(fixture_id, set()).add(pairs[offset])
    return {
        graph.capabilities[fixture_id].fixture.name
        for fixture_id, seen in levels.items()
        if len(seen) > 1
    }
