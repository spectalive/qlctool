"""The uncached walk behind `reach`: every channel through this function's descendants."""

from .driven_channels import Driven
from .higher import higher
from .show_graph import ShowGraph


def uncached_reach(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    kinds: tuple[str, ...] | None,
) -> Driven:
    merged: Driven = {}
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None:
            continue
        if kinds is not None and function.attrib.get("Type") not in kinds:
            continue
        for fixture_id, pairs in graph.driven(member, groups).items():
            target = merged.setdefault(fixture_id, {})
            for offset, value in pairs.items():
                target[offset] = higher(target.get(offset, 0), value)
    return merged
