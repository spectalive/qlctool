"""Functions a solo frame stops each other from starting, but that also start each other."""

from lxml import etree

from ..xmlutil import localname
from .function_of import function_of
from .positioned_widgets import positioned_widgets
from .show_graph import ShowGraph


def solo_frame_clashes(graph: ShowGraph, frame: etree._Element) -> list[tuple[str, str, str]]:
    """(clashing function's name, frame caption, the names it clashes with)."""
    found: list[tuple[str, str, str]] = []
    for widget, _, _ in positioned_widgets(frame):
        if localname(widget) != "SoloFrame":
            continue
        inside = {
            function_id
            for child in widget
            if localname(child) == "Button" and (function_id := function_of(child)) is not None
        }
        for function_id in sorted(inside):
            clash = (graph.descendants(function_id) - {function_id}) & inside
            if clash:
                found.append(
                    (
                        graph.name(function_id),
                        widget.attrib.get("Caption", ""),
                        ", ".join(graph.name(c) for c in sorted(clash)),
                    )
                )
    return found
