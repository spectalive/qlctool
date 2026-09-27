"""Cache the problems and handoffs computed for one graph and room states."""

from lxml import etree

from .handoff import Handoff
from .problem import Problem
from .show_graph import ShowGraph

# One frame's problems and handoff, per graph and room states: the layer rules
# ask about every button, and each button used to re-read its whole frame.
_FRAME_CACHE: list[
    tuple[
        ShowGraph,
        object,
        frozenset[int],
        dict[etree._Element, tuple[Problem, ...] | None],
        dict[etree._Element, Handoff | None],
    ]
] = []


def frame_memo(
    graph: ShowGraph, groups: object, states: set[int]
) -> tuple[
    dict[etree._Element, tuple[Problem, ...] | None],
    dict[etree._Element, Handoff | None],
]:
    state_ids = frozenset(states)
    if _FRAME_CACHE:
        cached_graph, cached_groups, cached_states, problems, handoffs = _FRAME_CACHE[0]
        if cached_graph is graph and cached_groups is groups and cached_states == state_ids:
            return problems, handoffs
    problems, handoffs = {}, {}
    _FRAME_CACHE[:] = [(graph, groups, state_ids, problems, handoffs)]
    return problems, handoffs
