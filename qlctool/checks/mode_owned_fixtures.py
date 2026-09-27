"""Fixtures whose mode channel every lighting room state drives."""

from .. import roles
from ..internal_program import internal_program
from .show_graph import ShowGraph, lit, reach


def mode_owned_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int]
) -> set[int]:
    """Fixtures whose mode channel every lighting room state drives.

    Owned means deterministic: whichever state is running, something in it is
    writing the mode channel, so a colour scene's RGB reads or is ignored by
    that state's decision - never by whatever ran before. A state that keeps
    the fixture dark is excused the way `rule_accent_restore` excuses it. No
    states, no owners: the rule then demands the mode-off write in the scene
    itself, exactly as before.
    """
    if not states:
        return set()
    state_reach = [reach(graph, groups, state_id) for state_id in states]
    owned: set[int] = set()
    for fixture_id, capability in graph.capabilities.items():
        program = internal_program(capability)
        if program is None:
            continue
        dimmers = capability.offsets_for_role(roles.DIMMER)
        lighting = [
            driven
            for driven in state_reach
            if any(lit(driven.get(fixture_id, {}).get(offset, 0)) for offset in dimmers)
        ]
        if lighting and all(
            program.mode_offset in driven.get(fixture_id, {}) for driven in lighting
        ):
            owned.add(fixture_id)
    return owned
