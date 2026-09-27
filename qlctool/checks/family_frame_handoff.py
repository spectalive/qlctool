"""The graph-derived members and hooks of one semantic family frame."""

from lxml import etree

from ..xmlutil import localname
from .frame_memo import frame_memo
from .handoff import Handoff
from .raw_frame_handoff import raw_frame_handoff
from .show_graph import ShowGraph
from .solo_frame_of_or_self import solo_frame_of_or_self


def family_frame_handoff(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    states: set[int],
    widget: etree._Element | None,
) -> Handoff | None:
    frame = solo_frame_of_or_self(widget)
    if frame is None or localname(frame) != "SoloFrame":
        return None
    _, handoffs = frame_memo(graph, groups, states)
    if frame not in handoffs:
        handoffs[frame] = raw_frame_handoff(graph, groups, states, frame)
    return handoffs[frame]
