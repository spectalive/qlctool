"""(fixture name, value written, the endpoint it should have written)."""

from ..shutter_open import shutter_open_ranges
from ..shutter_open_value import shutter_open_value
from .show_graph import ShowGraph


def short_of_the_endpoint(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> list[tuple[str, int, int]]:
    """(fixture name, value written, the endpoint it should have written)."""
    driven = graph.driven_of(graph.functions[function_id], groups)
    short: list[tuple[str, int, int]] = []
    for fixture_id, written in driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        for offset, opening in shutter_open_ranges(capability):
            value = written.get(offset)
            if value is None:
                continue
            endpoint = shutter_open_value(opening)
            if opening.minimum <= value <= opening.maximum and value != endpoint:
                short.append((capability.fixture.name, value, endpoint))
    return short
