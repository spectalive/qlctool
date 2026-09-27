"""The fixtures a narrower colour clock paints, next to the widest one."""

from .show_graph import ShowGraph
from .step_colours import step_colours


def stray_clock_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], clock_ids: set[int]
) -> tuple[str, ...]:
    """The fixtures the narrower clocks paint: the group off on its own beat."""
    painted = {
        clock: {
            item[0]
            for step in graph.members.get(clock, ())
            for item in step_colours(graph, groups, step)
        }
        for clock in clock_ids
    }
    widest = max(painted, key=lambda clock: len(painted[clock]))
    stray = set().union(*(fixtures for clock, fixtures in painted.items() if clock != widest))
    return tuple(
        sorted(
            graph.capabilities[fixture_id].fixture.name
            for fixture_id in stray
            if fixture_id in graph.capabilities
        )
    )
