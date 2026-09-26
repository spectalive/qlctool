"""The rules that read what moves the heads.

Where a family's figures go (`movement_families`, `movement_window`,
`unaimed_movement`), whether the automatic show parks one family beside a
moving one (`parked_movers`), and whether two buttons of one frame move the
rigged heads alike (`twin_movement`). Run together, in that order, which is
the order `check_workspace` always ran them in.
"""

from lxml import etree

from .finding import Finding
from .rule_movement_families import check_movement_families
from .rule_movement_window import check_movement_window
from .rule_parked_movers import check_parked_movers
from .rule_twin_movement import check_twin_movement
from .rule_unaimed_movement import check_unaimed_movement
from .show_graph import ShowGraph


def movement_findings(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    """Every movement rule's findings."""
    return [
        *check_movement_families(graph),
        *check_parked_movers(graph),
        *check_unaimed_movement(graph),
        *check_movement_window(graph),
        *check_twin_movement(graph, root),
    ]
