"""Walk a function's members, collecting leaves reached through a Chaser step."""

from .show_graph import ShowGraph


def collect_stepped_leaves(
    graph: ShowGraph, function_id: int, stepped: bool, seen: set[int], found: set[int]
) -> None:
    if function_id in seen:
        return
    function = graph.functions.get(function_id)
    if function is None:
        return
    members = graph.members.get(function_id, ())
    if not members:
        if stepped:
            found.add(function_id)
        return
    via_chaser = stepped or function.attrib.get("Type") == "Chaser"
    for member in members:
        collect_stepped_leaves(graph, member, via_chaser, seen | {function_id}, found)
