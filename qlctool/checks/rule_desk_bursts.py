"""2026-09-13: a lost tablet release must never leave a held accent running."""

from lxml import etree

from ..desk_burst_buttons import desk_burst_buttons
from ..desk_burst_duration import desk_burst_duration
from ..desk_burst_sources import desk_burst_sources
from ..names.default_names import default_names
from ..names.names import Names
from .desk_burst_errors import desk_burst_errors
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "rafaga del desk"


def check_desk_bursts(
    graph: ShowGraph, root: etree._Element, names: Names | None = None
) -> list[Finding]:
    vocabulary = default_names() if names is None else names
    sources = desk_burst_sources(root, vocabulary)
    buttons = desk_burst_buttons(root, vocabulary)
    findings = []
    for key in sources.keys() | buttons.keys():
        candidates = buttons.get(key, [])
        duration = desk_burst_duration(sources[key], vocabulary) if key in sources else None
        if duration is None or len(candidates) != 1:
            findings.append(
                Finding(
                    RULE, ERROR, key, "requiere un origen, una duracion y un unico Toggle de rafaga"
                )
            )
            continue
        for error in desk_burst_errors(graph, root, sources[key], candidates[0], duration):
            findings.append(Finding(RULE, ERROR, key, error))
    return findings
