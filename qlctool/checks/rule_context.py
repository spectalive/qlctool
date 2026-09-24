"""What one pass over a workspace has already worked out, handed to a provider's rules."""

from collections.abc import Mapping
from dataclasses import dataclass

from lxml import etree

from .show_graph import ShowGraph


@dataclass(frozen=True)
class RuleContext:
    """The workspace root, its function graph, groups, console entry points and room states."""

    root: etree._Element
    graph: ShowGraph
    groups: Mapping[int, tuple[int, ...]]
    entries: Mapping[int, str]
    states: set[int]
