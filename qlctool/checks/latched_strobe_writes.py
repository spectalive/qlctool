"""Strobe writes of a Flash scene, and the states that leave each one latched."""

from lxml import etree

from .. import roles
from .instant_evaluator import InstantEvaluator
from .show_graph import ShowGraph
from .strobe_written import strobe_capable_offsets
from .unowned_while_lit import unowned_while_lit
from .value_strobes import value_strobes


def latched_strobe_writes(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    scene: etree._Element,
    states: set[int],
    evaluator: InstantEvaluator,
) -> dict[str, tuple[str, ...]]:
    """Fixture name -> the states that leave its strobe writes latched, strobed only."""
    found: dict[str, tuple[str, ...]] = {}
    for fixture_id, written in graph.driven_of(scene, groups).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke:
            continue
        strobed = {
            offset
            for offset, strobing in strobe_capable_offsets(capability).items()
            if (value := written.get(offset)) is not None and value_strobes(strobing, value)
        }
        if not strobed:
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
                    frozenset(strobed),
                    tuple(dimmers),
                    evaluator=evaluator,
                )
            )
        )
        if not orphan_states:
            continue
        found[capability.fixture.name] = orphan_states
    return found
