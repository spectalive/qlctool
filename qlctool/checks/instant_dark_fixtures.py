"""Fixtures left dark by one concurrent graph instant."""

from .. import roles
from ..shutter_open import shutter_open_ranges
from ..strobe_range import strobe_range
from .color_roles import COLOUR
from .instant_evaluator import InstantEvaluator
from .show_graph import ShowGraph, lit, merge, reach
from .shutter_closed_while_lit import shutter_closed_while_lit
from .unowned_instant import unowned_while_lit


def instant_dark_fixtures(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_ids: tuple[int, ...],
    stopped: frozenset[int] = frozenset(),
    check_shutters: bool = False,
    evaluator: InstantEvaluator | None = None,
) -> list[str]:
    """Fixtures a concurrent instant colours while leaving intensity dark."""
    active_evaluator = evaluator or InstantEvaluator(graph, groups)
    colour_driven = {}
    for function_id in function_ids:
        colour_driven = merge(colour_driven, reach(graph, groups, function_id))
    dark: list[str] = []
    for fixture_id, written in colour_driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or (capability.is_smoke and not capability.is_lit_smoke):
            continue
        coloured = tuple(
            offset
            for role in COLOUR
            for offset in capability.offsets_for_role(role)
            if offset in written and lit(written[offset])
        )
        if not coloured:
            continue
        dimmers = capability.offsets_for_role(roles.DIMMER)
        if dimmers and unowned_while_lit(
            graph,
            groups,
            function_ids,
            fixture_id,
            frozenset(dimmers),
            coloured,
            stopped,
            evaluator=active_evaluator,
        ):
            dark.append(capability.fixture.name)
            continue
        if check_shutters and any(
            shutter_closed_while_lit(
                graph,
                groups,
                function_ids,
                fixture_id,
                coloured,
                offset,
                lambda value, opening=opening, ranges=capability.capabilities_by_offset[offset]: (
                    _shut(value, opening, strobe_range(ranges))
                ),
                stopped,
                evaluator=active_evaluator,
            )
            for offset, opening in shutter_open_ranges(capability)
        ):
            dark.append(capability.fixture.name)
    return dark


def _shut(value: int | None, opening, strobing) -> bool:
    if value is None:
        return False
    if opening.minimum <= value <= opening.maximum:
        return False
    return strobing is None or not (strobing.minimum <= value <= strobing.maximum)
