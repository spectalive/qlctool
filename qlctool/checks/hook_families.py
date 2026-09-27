"""Families written by every Toggle in one SoloFrame's function graph.

A frame is an operator boundary, not a semantic label: renamed frames and
one-member pick wrappers receive the same family contract as visible hooks.
"""

from lxml import etree

from .function_families import function_families
from .show_graph import ShowGraph


def hook_families(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], toggles: dict[int, etree._Element]
) -> set[str]:
    return {
        family
        for function_id in toggles
        for family, fixtures in function_families(graph, groups, function_id).items()
        if fixtures
    }
