"""The fixtures whose red, green or blue a look *animates*."""

from .. import roles
from .efx_animates_colour import efx_animates_colour
from .show_graph import ShowGraph


def animated_rgb_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> set[int]:
    animated: set[int] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or not efx_animates_colour(function):
            continue
        for fixture_id, pairs in graph.driven_of(function, groups).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            rgb = [
                offset
                for role in (roles.RED, roles.GREEN, roles.BLUE)
                for offset in capability.offsets_for_role(role)
            ]
            if any(offset in pairs for offset in rgb):
                animated.add(fixture_id)
    return animated
