"""The patch names of a set of fixture ids, sorted and without repeats, for a finding."""

from collections.abc import Iterable

from .show_graph import ShowGraph


def fixture_names_of(graph: ShowGraph, fixture_ids: Iterable[int]) -> tuple[str, ...]:
    return tuple(sorted({graph.capabilities[f].fixture.name for f in fixture_ids}))
