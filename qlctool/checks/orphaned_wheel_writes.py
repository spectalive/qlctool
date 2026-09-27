"""Wheel writes of a Flash scene, and the states that leave each one unowned."""

from lxml import etree

from .. import roles
from .instant_evaluator import InstantEvaluator
from .show_graph import ShowGraph
from .unowned_while_lit import unowned_while_lit

WHEEL_ROLES = (roles.COLOR_MACRO, roles.GOBO, roles.PRISM)


def orphaned_wheel_writes(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    scene: etree._Element,
    states: set[int],
    evaluator: InstantEvaluator,
) -> dict[str, tuple[str, ...]]:
    """Fixture name -> the states that leave its wheel writes unowned, touched only."""
    found: dict[str, tuple[str, ...]] = {}
    for fixture_id, written in graph.driven_of(scene, {}).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        wheels = {offset for role in WHEEL_ROLES for offset in capability.offsets_for_role(role)}
        touched = wheels & set(written)
        if not touched:
            continue
        dimmers = capability.offsets_for_role(roles.DIMMER)
        orphan_states = tuple(
            sorted(
                graph.name(state_id)
                for state_id in states
                if unowned_while_lit(
                    graph,
                    groups,
                    state_id,
                    fixture_id,
                    frozenset(touched),
                    tuple(dimmers),
                    evaluator=evaluator,
                )
            )
        )
        if not orphan_states:
            continue
        found[capability.fixture.name] = orphan_states
    return found
