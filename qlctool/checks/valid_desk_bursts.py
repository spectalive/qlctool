"""Only fully verified, manually triggered bursts may bypass the latch guard."""

from lxml import etree

from ..desk_burst_buttons import desk_burst_buttons
from ..desk_burst_duration import desk_burst_duration
from ..desk_burst_sources import desk_burst_sources
from ..names.default_names import default_names
from ..names.names import Names
from .desk_burst_errors import desk_burst_errors
from .show_graph import ShowGraph


def valid_desk_bursts(
    graph: ShowGraph, root: etree._Element, names: Names | None = None
) -> set[int]:
    vocabulary = default_names() if names is None else names
    sources = desk_burst_sources(root, vocabulary)
    valid = set()
    for key, buttons in desk_burst_buttons(root, vocabulary).items():
        duration = desk_burst_duration(sources[key], vocabulary) if key in sources else None
        if duration is None or len(buttons) != 1:
            continue
        button = buttons[0]
        if button.function is not None and not desk_burst_errors(
            graph, root, sources[key], button, duration
        ):
            valid.add(button.function)
    return valid
