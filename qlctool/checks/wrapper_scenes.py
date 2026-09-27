"""Resolve the Scene leaves that a Collection wrapper starts.

A wrapper is a one-member Collection, or - since ruling D7 put the washes-held
scene beside the fan and the cross (2026-09-26) - a Collection of Scenes only.
Anything else is a look built of several functions, not a wrapper.
"""

from .show_graph import ShowGraph


def wrapper_scenes(graph: ShowGraph, function_id: int) -> tuple[int, ...]:
    """The Scenes reached by a Scene or by its Collection wrapper."""
    function = graph.functions.get(function_id)
    if function is None:
        return ()
    if function.attrib.get("Type") == "Scene":
        return (function_id,)
    if function.attrib.get("Type") != "Collection":
        return ()
    members = graph.members.get(function_id, ())
    all_scenes = all(
        member in graph.functions and graph.functions[member].attrib.get("Type") == "Scene"
        for member in members
    )
    if len(members) != 1 and not (members and all_scenes):
        return ()
    return tuple(
        leaf_id
        for leaf_id in graph.descendants(function_id)
        if graph.functions[leaf_id].attrib.get("Type") == "Scene"
    )
