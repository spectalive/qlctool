"""Find incomplete solo frames that let an operator play one channel family."""

from collections.abc import Mapping
from dataclasses import dataclass

from lxml import etree

from .. import roles
from ..capability import FixtureCapabilities
from ..internal_program import internal_program
from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, localname
from .phrase import Phrase
from .show_graph import ShowGraph, reach
from .steps_are_levels import steps_are_levels

FAMILIES = {
    "color": frozenset(
        (
            roles.RED,
            roles.GREEN,
            roles.BLUE,
            roles.WHITE,
            roles.CYAN,
            roles.MAGENTA,
            roles.YELLOW,
            roles.COLOR_MACRO,
        )
    ),
    "position": frozenset((roles.PAN, roles.PAN_FINE, roles.TILT, roles.TILT_FINE)),
    "gobo": frozenset((roles.GOBO, roles.GOBO_SHAKE, roles.FOCUS)),
    "prism": frozenset((roles.PRISM, roles.PRISM_ROTATION)),
}
_OWNER_CACHE: list[
    tuple[ShowGraph, dict[int, tuple[int, ...]], frozenset[int], dict[str, set[int]]]
] = []
# The buttons, Toggles, hooks, hook families and owners of one family frame.
_Handoff = tuple[
    dict[int, etree._Element],
    dict[int, etree._Element],
    set[int],
    set[str],
    dict[str, set[int]],
]


@dataclass(frozen=True)
class _Problem:
    function_id: int
    # A `[findings]` entry and its fields (ruling B10, round 2).
    said: Phrase


# One frame's problems and handoff, per graph and room states: the layer rules
# ask about every button, and each button used to re-read its whole frame.
_FRAME_CACHE: list[
    tuple[
        ShowGraph,
        object,
        frozenset[int],
        dict[etree._Element, tuple[_Problem, ...] | None],
        dict[etree._Element, _Handoff | None],
    ]
] = []


def family_frame_problems(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    states: set[int],
    widget: etree._Element | None,
) -> tuple[_Problem, ...] | None:
    """Problems in a family SoloFrame, or None when the frame has no hook."""
    frame = _solo_frame_of(widget)
    if frame is None:
        return None
    problems, _ = _frame_memo(graph, groups, states)
    if frame not in problems:
        problems[frame] = _frame_problems(graph, groups, states, frame)
    return problems[frame]


def _frame_problems(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int], frame: etree._Element
) -> tuple[_Problem, ...] | None:
    handoff = _family_frame_handoff(graph, groups, states, frame)
    if handoff is None:
        return None
    buttons, toggles, hooks, hook_families, owners = handoff

    problems: list[_Problem] = []
    for family in sorted(hook_families):
        for function_id in sorted(owners[family] - set(toggles)):
            problems.append(_Problem(function_id, Phrase("family_owner_no_toggle")))
    state_reachable = set().union(*(graph.descendants(state_id) for state_id in states))
    for function_id in sorted(set(toggles) - hooks):
        if function_id in state_reachable:
            problems.append(_Problem(function_id, Phrase("family_owner_state_pick")))
    for hook_id in sorted(hooks):
        starters = sorted(
            function_id
            for function_id in buttons
            if function_id != hook_id and hook_id in graph.descendants(function_id)
        )
        for function_id in starters:
            problems.append(
                _Problem(
                    function_id,
                    Phrase("family_owner_starts_hook", {"hook": graph.name(hook_id)}),
                )
            )
    return tuple(problems)


def _family_frame_handoff(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    states: set[int],
    widget: etree._Element | None,
) -> _Handoff | None:
    """The graph-derived members and hooks of one semantic family frame."""
    frame = _solo_frame_of(widget)
    if frame is None or localname(frame) != "SoloFrame":
        return None
    _, handoffs = _frame_memo(graph, groups, states)
    if frame not in handoffs:
        handoffs[frame] = _frame_handoff(graph, groups, states, frame)
    return handoffs[frame]


def _frame_memo(
    graph: ShowGraph, groups: object, states: set[int]
) -> tuple[
    dict[etree._Element, tuple[_Problem, ...] | None],
    dict[etree._Element, _Handoff | None],
]:
    state_ids = frozenset(states)
    if _FRAME_CACHE:
        cached_graph, cached_groups, cached_states, problems, handoffs = _FRAME_CACHE[0]
        if cached_graph is graph and cached_groups is groups and cached_states == state_ids:
            return problems, handoffs
    problems, handoffs = {}, {}
    _FRAME_CACHE[:] = [(graph, groups, state_ids, problems, handoffs)]
    return problems, handoffs


def _frame_handoff(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int], frame: etree._Element
) -> _Handoff | None:
    buttons = _buttons(frame)
    toggles = {function_id: button for function_id, button in buttons.items() if _is_toggle(button)}
    owners = _cached_state_owners(graph, groups, states)
    owner_ids = set().union(*owners.values())
    if not (set(toggles) & owner_ids) or set(toggles) <= states:
        return None
    hook_families = _hook_families(graph, groups, toggles)
    if not hook_families:
        return None
    hooks = set().union(*(owners[family] for family in hook_families)) & set(toggles)
    return buttons, toggles, hooks, hook_families, owners


def _hook_families(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], toggles: dict[int, etree._Element]
) -> set[str]:
    """Families written by every Toggle in one SoloFrame's function graph.

    A frame is an operator boundary, not a semantic label: renamed frames and
    one-member pick wrappers receive the same family contract as visible hooks.
    """
    return {
        family
        for function_id in toggles
        for family, fixtures in _function_families(graph, groups, function_id).items()
        if fixtures
    }


def _buttons(frame: etree._Element) -> dict[int, etree._Element]:
    found: dict[int, etree._Element] = {}
    for button in frame.iter():
        if localname(button) != "Button":
            continue
        if _solo_frame_of(button) is not frame:
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id != NO_FUNCTION:
            found[function_id] = button
    return found


def _is_toggle(button: etree._Element) -> bool:
    action = find_local(button, "Action")
    return action is None or (action.text or "").strip() in ("", "Toggle")


def _state_owners(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int]
) -> dict[str, set[int]]:
    families = (*FAMILIES, "pixel-mode")
    owners: dict[str, set[int]] = {family: set() for family in families}
    for state_id in states:
        for function_id in _owner_frontier(graph, groups, state_id):
            for family in _owner_families(graph, groups, function_id):
                owners[family].add(function_id)
    return owners


def _owner_families(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> tuple[str, ...]:
    """Every family a direct functional state owner can restore."""
    families = tuple(
        family
        for family, fixtures in _function_families(graph, groups, function_id).items()
        if fixtures
    )
    if graph.kind(function_id) in ("Chaser", "Sequence") and (
        len(families) > 1 or steps_are_levels(graph, function_id)
    ):
        return ()
    return families


def _cached_state_owners(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int]
) -> dict[str, set[int]]:
    state_ids = frozenset(states)
    if _OWNER_CACHE:
        cached_graph, cached_groups, cached_states, owners = _OWNER_CACHE[0]
        if cached_graph is graph and cached_groups is groups and cached_states == state_ids:
            return owners
    owners = _state_owners(graph, groups, states)
    _OWNER_CACHE[:] = [(graph, groups, state_ids, owners)]
    return owners


def _owner_frontier(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], state_id: int
) -> set[int]:
    """Functions whose starts can return one family to its room-state owner.

    A multi-family Chaser/Sequence coordinates structural level Collections;
    recurse through those until one family has its actual owner. A single-family
    Collection or Chaser such as `Movimientos Suaves` or `Gobo Animacion`
    remains the functional owner, never its leaf steps. A Chaser whose steps
    are all level Collections is structural too, even with one family
    (`steps_are_levels`, 2026-09-25).
    """
    found: set[int] = set()
    for function_id in graph.members.get(state_id, ()):
        found.update(_nested_owner_frontier(graph, groups, function_id, False, set()))
    return found


def _nested_owner_frontier(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    inside_structural_cycle: bool,
    seen: set[int],
    level_step: bool = False,
) -> set[int]:
    """Flatten only the multi-family level containers inside a state cycle."""
    if function_id in seen:
        return set()
    families = tuple(
        family
        for family, fixtures in _function_families(graph, groups, function_id).items()
        if fixtures
    )
    kind = graph.kind(function_id)
    is_cycle = kind in ("Chaser", "Sequence") and (
        len(families) > 1 or steps_are_levels(graph, function_id)
    )
    is_level = (
        kind == "Collection" and inside_structural_cycle and (len(families) > 1 or level_step)
    )
    if not (is_cycle or is_level):
        return {function_id}
    nested_seen = {*seen, function_id}
    found: set[int] = set()
    for member_id in graph.members.get(function_id, ()):
        found.update(
            _nested_owner_frontier(
                graph,
                groups,
                member_id,
                True,
                nested_seen,
                is_cycle and steps_are_levels(graph, function_id),
            )
        )
    return found


def _function_families(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> dict[str, set[int]]:
    found: dict[str, set[int]] = {family: set() for family in FAMILIES}
    found["pixel-mode"] = set()
    for fixture_id, written in reach(graph, groups, function_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        written_roles = {capability.roles_by_offset[offset] for offset in written}
        for family, family_roles in FAMILIES.items():
            if written_roles & family_roles:
                found[family].add(fixture_id)
        if _sets_pixel_mode(capability, written):
            found["pixel-mode"].add(fixture_id)
    return found


def _is_pixel_fixture(capability: FixtureCapabilities) -> bool:
    moving_roles = FAMILIES["position"]
    return (
        not capability.is_smoke
        and bool(capability.roles & FAMILIES["color"])
        and not bool(capability.roles & moving_roles)
        and internal_program(capability) is not None
    )


def _sets_pixel_mode(capability: FixtureCapabilities, written: Mapping[int, int | None]) -> bool:
    """The look writes the mode channel of a fixture's named internal programme.

    Not any Effect channel: every colour look parks a stray self-running
    channel at zero (`mode_park_pairs`), and on an RGB par with one "auto
    show" channel that made every colour scene a pixel-mode owner, so a
    single-model rig's colour frame could never be complete (round G review,
    2026-09-26: the CLB2.4 in its 2 and 7 channel modes).
    """
    program = internal_program(capability) if _is_pixel_fixture(capability) else None
    return program is not None and program.mode_offset in written


def _solo_frame_of(widget: etree._Element | None) -> etree._Element | None:
    current = widget
    while current is not None:
        if localname(current) == "SoloFrame":
            return current
        current = current.getparent()
    return None
