"""Build one family frame's members and hooks straight from the graph."""

from lxml import etree

from .cached_state_owners import cached_state_owners
from .handoff import Handoff
from .hook_families import hook_families
from .is_toggle import is_toggle
from .show_graph import ShowGraph
from .solo_frame_buttons import solo_frame_buttons


def raw_frame_handoff(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int], frame: etree._Element
) -> Handoff | None:
    buttons = solo_frame_buttons(frame)
    toggles = {function_id: button for function_id, button in buttons.items() if is_toggle(button)}
    owners = cached_state_owners(graph, groups, states)
    owner_ids = set().union(*owners.values())
    if not (set(toggles) & owner_ids) or set(toggles) <= states:
        return None
    families = hook_families(graph, groups, toggles)
    if not families:
        return None
    hooks = set().union(*(owners[family] for family in families)) & set(toggles)
    return buttons, toggles, hooks, families, owners
