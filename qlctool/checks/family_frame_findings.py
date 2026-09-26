"""The rules that read a family SoloFrame's hooks and latched picks.

Whether the frame is complete (`family_owner`), whether a pick's start leaves
the room dark (`pick_darkens`), and whether its release leaves part of its
family with no owner (`pick_release_orphans`). Run together, in that order.
"""

from lxml import etree

from .finding import Finding
from .rule_family_owner import check_family_owner
from .rule_pick_darkens import check_pick_darkens
from .rule_pick_release_orphans import check_pick_release_orphans
from .show_graph import ShowGraph


def family_frame_findings(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    states: set[int],
) -> list[Finding]:
    """Every family-frame rule's findings."""
    return [
        *check_family_owner(graph, groups, root, states),
        *check_pick_darkens(graph, groups, root, states),
        *check_pick_release_orphans(graph, groups, root, states),
    ]
