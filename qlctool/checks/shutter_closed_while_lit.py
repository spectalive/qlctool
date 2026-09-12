"""Detect a labelled shutter left closed beside running colour."""

from collections.abc import Callable

from .instant_evaluator import InstantEvaluator
from .show_graph import ShowGraph


def shutter_closed_while_lit(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_ids: int | tuple[int, ...],
    fixture_id: int,
    colour_offsets: tuple[int, ...],
    offset: int,
    is_closed: Callable[[int | None], bool],
    stopped: frozenset[int],
    evaluator: InstantEvaluator | None = None,
) -> bool:
    """Whether a labelled shutter can remain closed while colour is present."""
    active_evaluator = evaluator or InstantEvaluator(graph, groups)
    return any(
        state.coloured and is_closed(state.value if state.written else 0)
        for state in active_evaluator.states(
            function_ids,
            fixture_id,
            offset,
            colour_offsets,
            stopped,
        )
    )
