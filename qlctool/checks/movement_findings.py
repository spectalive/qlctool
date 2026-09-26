"""The rules that read what moves the heads.

Where a family's figures go (`movement_families`, `movement_window`,
`unaimed_movement`), whether the automatic show parks one family beside a
moving one (`parked_movers`), and whether two buttons of one frame move the
rigged heads alike (`twin_movement`), and whether an instant the console can
make leaves a rigged head with nothing aiming it (`unaimed_rigged_mover`).
Run together, in that order; the first four in the order `check_workspace`
always ran them.
"""

from lxml import etree

from .finding import Finding
from .rule_movement_families import check_movement_families
from .rule_movement_window import check_movement_window
from .rule_parked_movers import check_parked_movers
from .rule_twin_movement import check_twin_movement
from .rule_unaimed_movement import check_unaimed_movement
from .rule_unaimed_rigged_mover import check_unaimed_rigged_mover
from .show_graph import ShowGraph


def movement_findings(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    states: set[int],
) -> list[Finding]:
    """Every movement rule's findings."""
    return [
        *check_movement_families(graph),
        *check_parked_movers(graph),
        *check_unaimed_movement(graph),
        *check_movement_window(graph),
        *check_twin_movement(graph, root),
        *check_unaimed_rigged_mover(graph, groups, root, states),
    ]
