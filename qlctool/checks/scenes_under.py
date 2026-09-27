"""The Scenes reachable under a function, looking only through Collections."""

from .show_graph import ShowGraph


def scenes_under(graph: ShowGraph, function_id: int) -> list[int]:
    kind = graph.kind(function_id)
    if kind == "Scene":
        return [function_id]
    if kind != "Collection":
        return []
    found: list[int] = []
    for member in graph.members.get(function_id, ()):
        found += scenes_under(graph, member)
    return found
