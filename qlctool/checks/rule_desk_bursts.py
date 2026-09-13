"""2026-09-13: a lost tablet release must never leave a held accent running."""

from lxml import etree

from ..desk_burst_buttons import desk_burst_buttons
from ..desk_burst_sources import desk_burst_sources
from ..desk_policy import BURST_MS
from .desk_burst_errors import desk_burst_errors
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "rafaga del desk"


def check_desk_bursts(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    sources = desk_burst_sources(root)
    buttons = desk_burst_buttons(root)
    findings = []
    for key in sources.keys() | buttons.keys():
        candidates = buttons.get(key, [])
        if key not in sources or key not in BURST_MS or len(candidates) != 1:
            findings.append(
                Finding(
                    RULE, ERROR, key, "requiere un origen, una duracion y un unico Toggle de rafaga"
                )
            )
            continue
        for error in desk_burst_errors(graph, root, sources[key], candidates[0], BURST_MS[key]):
            findings.append(Finding(RULE, ERROR, key, error))
    return findings
