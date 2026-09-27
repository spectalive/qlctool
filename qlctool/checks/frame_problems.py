"""The problems one family SoloFrame's handoff turns up, if it has any."""

from lxml import etree

from .family_frame_handoff import family_frame_handoff
from .phrase import Phrase
from .problem import Problem
from .show_graph import ShowGraph


def frame_problems(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int], frame: etree._Element
) -> tuple[Problem, ...] | None:
    handoff = family_frame_handoff(graph, groups, states, frame)
    if handoff is None:
        return None
    buttons, toggles, hooks, hook_families, owners = handoff

    problems: list[Problem] = []
    for family in sorted(hook_families):
        for function_id in sorted(owners[family] - set(toggles)):
            problems.append(Problem(function_id, Phrase("family_owner_no_toggle")))
    state_reachable = set().union(*(graph.descendants(state_id) for state_id in states))
    for function_id in sorted(set(toggles) - hooks):
        if function_id in state_reachable:
            problems.append(Problem(function_id, Phrase("family_owner_state_pick")))
    for hook_id in sorted(hooks):
        starters = sorted(
            function_id
            for function_id in buttons
            if function_id != hook_id and hook_id in graph.descendants(function_id)
        )
        for function_id in starters:
            problems.append(
                Problem(
                    function_id,
                    Phrase("family_owner_starts_hook", {"hook": graph.name(hook_id)}),
                )
            )
    return tuple(problems)
