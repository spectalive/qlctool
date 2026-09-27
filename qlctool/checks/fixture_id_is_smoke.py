"""Whether a driven fixture, looked up by id in the graph, is a smoke machine."""

from .show_graph import ShowGraph


def fixture_id_is_smoke(graph: ShowGraph, fixture_id: int) -> bool:
    capability = graph.capabilities.get(fixture_id)
    return capability is not None and capability.is_smoke
