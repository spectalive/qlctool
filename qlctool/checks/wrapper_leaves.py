"""Resolve the Scene leaves that a single-member Collection wrapper starts."""

from .show_graph import ShowGraph


def wrapper_scenes(graph: ShowGraph, function_id: int) -> tuple[int, ...]:
    """The Scenes reached by a Scene or by its one-member Collection wrapper."""
    function = graph.functions.get(function_id)
    if function is None:
        return ()
    if function.attrib.get("Type") == "Scene":
        return (function_id,)
    if function.attrib.get("Type") != "Collection" or len(graph.members.get(function_id, ())) != 1:
        return ()
    return tuple(
        leaf_id
        for leaf_id in graph.descendants(function_id)
        if graph.functions[leaf_id].attrib.get("Type") == "Scene"
    )
