"""Fixture names a scene lights without writing their zoom channel."""

from ..zoom_wide_pairs import zoom_wide_pairs
from .scene_lights_fixture import scene_lights_fixture
from .show_graph import ShowGraph


def lit_without_zoom(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> list[str]:
    driven = graph.driven_of(graph.functions[function_id], groups)
    names: list[str] = []
    for fixture_id, written in driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        zoom = zoom_wide_pairs(capability)
        if not zoom:
            continue
        if all(offset in written for offset, _ in zoom):
            continue
        if scene_lights_fixture(capability, written):
            names.append(capability.fixture.name)
    return names
