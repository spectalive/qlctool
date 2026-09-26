"""The pans one Scene gives the rigged movers, per family, read across the stage.

A family is told apart the way `rule_movement_families` does it: a mover with
a gobo wheel is a beam, one without is a wash - a raw pan value means nothing
across models. Only rigged heads the stage plot has placed are read: a spare
in a flight case has no place in the row, and neither has a head nobody put
on the plot.
"""

from collections.abc import Collection, Mapping

from .. import roles
from .show_graph import ShowGraph


def stage_pan_rows(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    rigged: Collection[int],
    positions: Mapping[int, float],
) -> list[list[tuple[int, int]]]:
    """(fixture id, pan) per family, each row in stage x order."""
    rows: dict[bool, list[tuple[float, int, int]]] = {}
    for fixture_id, written in graph.driven(function_id, groups).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or fixture_id not in rigged or fixture_id not in positions:
            continue
        if not capability.has_role(roles.TILT):
            continue
        pans = capability.offsets_for_role(roles.PAN)
        pan = written.get(pans[0]) if pans else None
        if pan is None:
            continue
        beam = capability.has_role(roles.GOBO)
        rows.setdefault(beam, []).append((positions[fixture_id], fixture_id, pan))
    return [
        [(fixture_id, pan) for _, fixture_id, pan in sorted(row)] for _, row in sorted(rows.items())
    ]
