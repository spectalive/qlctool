"""A split movement: a Collection whose every member is an EFX."""

from .show_graph import ShowGraph


def only_efx(graph: ShowGraph, function_id: int) -> bool:
    members = graph.members.get(function_id, ())
    return bool(members) and all(graph.kind(member) == "EFX" for member in members)
