"""Find incomplete solo frames that let an operator play one channel family."""

from lxml import etree

from .frame_memo import frame_memo
from .frame_problems import frame_problems
from .problem import Problem
from .show_graph import ShowGraph
from .solo_frame_of_or_self import solo_frame_of_or_self


def family_frame_problems(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    states: set[int],
    widget: etree._Element | None,
) -> tuple[Problem, ...] | None:
    """Problems in a family SoloFrame, or None when the frame has no hook."""
    frame = solo_frame_of_or_self(widget)
    if frame is None:
        return None
    problems, _ = frame_memo(graph, groups, states)
    if frame not in problems:
        problems[frame] = frame_problems(graph, groups, states, frame)
    return problems[frame]
