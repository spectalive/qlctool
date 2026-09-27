"""The fixture names an EFX drives, for the untempoed-rhythm rule's report."""

from .show_graph import ShowGraph


def efx_fixture_names(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> set[str]:
    function = graph.functions[function_id]
    return {
        graph.capabilities[fixture_id].fixture.name
        for fixture_id in graph.driven_of(function, groups)
        if fixture_id in graph.capabilities
    }
