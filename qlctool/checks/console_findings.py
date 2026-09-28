"""The rules that read the hand-built console itself.

Whether its layout is well-formed (`console`), whether a caption on it is
stale or missing (`console_caption`), whether the help frame names every key
it should (`help_names_frame`), and whether a key binding points at something
that still exists (`key_binding`). Run together, in that order - the last four
calls `check_workspace` always made.
"""

from lxml import etree

from .canvas_of import canvas_of
from .console_caption_findings import console_caption_findings
from .finding import Finding
from .key_binding_findings import key_binding_findings
from .rule_console import check_console
from .rule_help_names_frame import check_help_names_frame
from .show_graph import ShowGraph


def console_findings(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    states: set[int],
    canvas: tuple[int, int] | None,
) -> list[Finding]:
    """Every console rule's findings, in the order check_workspace ran them."""
    return [
        *check_console(graph, root, canvas or canvas_of(root)),
        *console_caption_findings(graph, root),
        *check_help_names_frame(root),
        *key_binding_findings(graph, groups, root, states),
    ]
