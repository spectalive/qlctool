"""Write each latched pick's per-state `releaseTo` into the desk map's controls."""

from typing import Any

from lxml import etree

from .checks.console_states import room_states
from .checks.show_graph import ShowGraph
from .desk_release_hooks import desk_release_hooks


def attach_release_hooks(
    controls: dict[str, dict[str, Any]],
    root: etree._Element,
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
) -> None:
    """Add `releaseTo` to every control that is a latched pick of a family frame.

    Optional, schema 2 unchanged: the desk ignores keys it does not know.
    """
    states = room_states(root, graph, groups)
    state_widgets = {
        c["function"]: c["widget"]
        for c in controls.values()
        if c["role"] == "state" and c["function"] in states
    }
    release = desk_release_hooks(graph, groups, root, states, state_widgets)
    for control in controls.values():
        if control["widget"] in release:
            control["releaseTo"] = release[control["widget"]]
