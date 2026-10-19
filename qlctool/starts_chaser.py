"""Whether a function starts a Chaser anywhere below it, itself included."""

from .checks.show_graph import ShowGraph


def starts_chaser(graph: ShowGraph, function_id: int) -> bool:
    return any(graph.kind(member) == "Chaser" for member in graph.descendants(function_id))
