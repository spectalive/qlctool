"""The hook the tablet presses, per room state, when a latched pick is released.

Picks stay latched (ruling D8, 2026-09-27): a pick stops its frame's hook, and
toggling it off restarts nothing, since QLC+ 5's solo frame has no restore.
The generator leaves the release clean - the family's floor under every state
takes the LTP channels back - but a clean release is the family at rest, not
the look the room was running. The tablet gets that back by pressing a hook,
and which hook depends on the state: under CHARLA the colour frame's hook is
`Luz Charla`, under FIESTA the heads' is `Movimientos Cabezas` (ruling R3a).

So a pick's `releaseTo` is an object: the decimal widget id of a room state's
control -> the widget id of the one hook of the pick's frame that state
starts. A state that starts none of the frame's hooks, or more than one (AUTO
on the heads, gobo and prism, whose hooks change with the energy level), is
left out: there the floor holds the family and the level's next step restarts
the right hook by itself. An empty object is not written. Hooks and states are
graph facts (`family_frame_handoff`, `ShowGraph.descendants`), not captions.

The desk's contract, written out for dmxdesk in `docs/desk-map.md`:
1. When a control carrying `releaseTo` is released (toggled off), look up the
   widget of the room state control that is on.
2. No entry for that state: press nothing.
3. Otherwise press `<hook>|255`, and only if that hook's widget is not
   already on - the hook is a Toggle, and pressing a running one stops it.

A control the desk places as a "hook" can carry `releaseTo` too: `Colores
simples` and its siblings are latched picks of the colour frame in the graph,
laid beside its hooks on the tablet.
"""

from collections.abc import Mapping

from lxml import etree

from .checks.family_frame_handoff import family_frame_handoff
from .checks.show_graph import ShowGraph
from .xmlutil import find_local, iter_local


def desk_release_hooks(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    states: set[int],
    state_widgets: Mapping[int, int],
) -> dict[int, dict[str, int]]:
    """Each family-frame pick's widget id -> {state widget id: hook widget id}.

    `states` are the room states (`room_states`); `state_widgets` maps those
    the desk shows to their control's widget id.
    """
    console = find_local(root, "VirtualConsole")
    release: dict[int, dict[str, int]] = {}
    for frame in iter_local(console, "SoloFrame") if console is not None else ():
        handoff = family_frame_handoff(graph, groups, states, frame)
        if handoff is None:
            continue
        buttons, toggles, hooks, _, _ = handoff
        by_state: dict[str, int] = {}
        for state_id, widget in sorted(state_widgets.items(), key=lambda item: item[1]):
            started = hooks & graph.descendants(state_id)
            if len(started) == 1:
                by_state[str(widget)] = int(buttons[next(iter(started))].attrib["ID"])
        if not by_state:
            continue
        for pick_id in set(toggles) - hooks:
            release[int(toggles[pick_id].attrib["ID"])] = dict(by_state)
    return release
