"""A solo frame deaf to its monitored buttons cannot hand a family over.

A solo frame stops every sibling's function when one of its widgets starts a
function - unless the frame *excludes monitored* buttons, in which case a
button that is only monitoring its function (started by something else, AUTO
for instance) is spared: QLC+ 5.2.2, `VCButton::notifyFunctionStarting`,
vcbutton.cpp:258.

That sparing is right for a library frame whose looks are the steps of a
chaser: each step's button reports its function starting, and without the
exclusion every step would cut the fade of the one before it. It is wrong for
a frame whose Toggles are hooks - chasers and collections that a room state
starts as children - because the whole point of such a frame is that a pick
pressed by hand stops the hook AUTO started. With the exclusion the hook is
Monitoring, is skipped, and the wheel keeps painting under the pick: two
colour sources on the rig (2026-09-12, found while building the tablet desk).
The same flag lets two haze timers share one pump, and lets a moment start
beside an AUTO that a duplicate button on another page had started.

The rule reasons about the graph, never about a caption: a solo frame must
hear its monitored buttons when a Toggle in it drives a branching function
(Chaser, Collection, Sequence) that some room state reaches, or a function
that another Toggle button outside the frame also drives.
"""

from lxml import etree

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local, localname
from .finding import ERROR, Finding
from .show_graph import BRANCHING, ShowGraph

RULE = "marco solo sordo"


def check_solo_handoff(graph: ShowGraph, root: etree._Element, states: set[int]) -> list[Finding]:
    findings: list[Finding] = []
    outside = _toggle_functions_by_frame(root)
    # What every room state reaches, computed once: the walk is the cost.
    reached = {state_id: graph.descendants(state_id) for state_id in states}
    for frame in iter_local(root, "SoloFrame"):
        toggles = outside.get(frame, set())
        if not toggles:
            continue
        exclude = find_local(frame, "ExcludeMonitored")
        if exclude is None or (exclude.text or "").strip() != "True":
            continue
        elsewhere = set().union(*(fns for other, fns in outside.items() if other is not frame))
        needing = sorted(
            function_id
            for function_id in toggles
            if _started_as_child(graph, reached, function_id) or function_id in elsewhere
        )
        if not needing:
            continue
        names = ", ".join(f"«{graph.name(function_id)}»" for function_id in needing[:3])
        findings.append(
            Finding(
                RULE,
                ERROR,
                frame.attrib.get("Caption", "") or f"SoloFrame {frame.attrib.get('ID', '?')}",
                "ignora a los botones que solo vigilan: otro estado o boton arranca "
                f"{names} y una eleccion del marco no lo apagara "
                "(ExcludeMonitored debe ser False)",
            )
        )
    return findings


def _started_as_child(graph: ShowGraph, reached: dict[int, set[int]], function_id: int) -> bool:
    """A branching function that a room state other than itself reaches."""
    if graph.kind(function_id) not in BRANCHING:
        return False
    return any(function_id in below for state_id, below in reached.items() if state_id != function_id)


def _toggle_functions_by_frame(root: etree._Element) -> dict[etree._Element | None, set[int]]:
    """The functions of every Toggle button, keyed by the solo frame holding it.

    Buttons outside any solo frame are keyed by None, which makes them count
    as "elsewhere" for every frame.
    """
    found: dict[etree._Element | None, set[int]] = {}
    for button in iter_local(root, "Button"):
        action = find_local(button, "Action")
        if action is not None and (action.text or "").strip() not in ("", "Toggle"):
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION:
            continue
        found.setdefault(_solo_frame_of(button), set()).add(function_id)
    return found


def _solo_frame_of(widget: etree._Element) -> etree._Element | None:
    current = widget.getparent()
    while current is not None:
        if localname(current) == "SoloFrame":
            return current
        current = current.getparent()
    return None
