"""Only fully verified, manually triggered bursts may bypass the latch guard."""

from lxml import etree

from ..desk_burst_buttons import desk_burst_buttons
from ..desk_burst_sources import desk_burst_sources
from ..desk_policy import BURST_MS
from .desk_burst_errors import desk_burst_errors
from .show_graph import ShowGraph


def valid_desk_bursts(graph: ShowGraph, root: etree._Element) -> set[int]:
    sources = desk_burst_sources(root)
    valid = set()
    for key, buttons in desk_burst_buttons(root).items():
        if key not in sources or key not in BURST_MS or len(buttons) != 1:
            continue
        button = buttons[0]
        if button.function is not None and not desk_burst_errors(
            graph, root, sources[key], button, BURST_MS[key]
        ):
            valid.add(button.function)
    return valid
