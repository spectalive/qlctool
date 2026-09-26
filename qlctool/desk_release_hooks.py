"""The hook the tablet presses when a latched pick of a family frame is released.

Picks stay latched (ruling D8, 2026-09-27): a pick stops its frame's hook, and
toggling it off restarts nothing, since QLC+ 5's solo frame has no restore.
The generator leaves the release clean - the family's floor under every state
takes the LTP channels back - but a clean release is the family at rest, not
the look the room was running. The tablet gets that back by pressing a hook.

A frame has several hooks, one per state or level that runs the family
(`Gobo Animacion` for FIESTA, `Gobo Reposo` for CHARLA). The map names one per
frame: the hook the most room states start, and between equals the first in
the frame - where the console lays the one AUTO's own looks use ("AUTO" in
its caption). The console's hooks are graph facts (`family_frame_handoff`),
not captions.
"""

from lxml import etree

from .checks.family_frames import family_frame_handoff
from .checks.show_graph import ShowGraph
from .xmlutil import find_local, iter_local


def desk_release_hooks(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element, states: set[int]
) -> dict[int, int]:
    """Each family-frame pick's widget id mapped to the widget id of its frame's hook."""
    console = find_local(root, "VirtualConsole")
    release: dict[int, int] = {}
    for frame in iter_local(console, "SoloFrame") if console is not None else ():
        handoff = family_frame_handoff(graph, groups, states, frame)
        if handoff is None:
            continue
        buttons, toggles, hooks, _, _ = handoff
        if not hooks:
            continue
        hook = min(
            hooks,
            key=lambda h: (
                -sum(1 for s in states if h in graph.descendants(s)),
                int(buttons[h].attrib["ID"]),
            ),
        )
        for pick_id in set(toggles) - hooks:
            release[int(toggles[pick_id].attrib["ID"])] = int(buttons[hook].attrib["ID"])
    return release
