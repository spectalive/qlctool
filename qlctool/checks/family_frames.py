"""Find incomplete solo frames that let an operator play one channel family."""

from dataclasses import dataclass

from lxml import etree

from .. import roles
from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, localname
from .show_graph import ShowGraph, reach

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
_OWNER_CACHE: list[tuple[ShowGraph, dict, frozenset[int], dict[str, set[int]]]] = []


@dataclass(frozen=True)
class _Problem:
    function_id: int
    message: str


def family_frame_problems(
    graph: ShowGraph, groups, states: set[int], widget: etree._Element | None
) -> tuple[_Problem, ...] | None:
    """Problems in a family SoloFrame, or None when the frame has no hook."""
    handoff = _family_frame_handoff(graph, groups, states, widget)
    if handoff is None:
        return None
    buttons, toggles, hooks, hook_families, owners = handoff

    problems: list[_Problem] = []
    for family in sorted(hook_families):
        for function_id in sorted(owners[family] - set(toggles)):
            problems.append(
                _Problem(
                    function_id,
                    "no tiene su Toggle en el marco: un estado de la sala tambien "
                    "escribe esa familia y al cambiar de estado la eleccion quedaria suelta",
                )
            )
    state_reachable = set().union(*(graph.descendants(state_id) for state_id in states))
    for function_id in sorted(set(toggles) - hooks):
        if function_id in state_reachable:
            problems.append(
                _Problem(
                    function_id,
                    "es un pick que un estado de la sala tambien arranca: el marco "
                    "solo lo apagara al arrancar ese estado",
                )
            )
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
                    f"arranca el hook «{graph.name(hook_id)}» del mismo marco solo: "
                    "el marco lo apagara nada mas pulsarlo",
                )
            )
    return tuple(problems)


def _family_frame_handoff(
    graph: ShowGraph, groups, states: set[int], widget: etree._Element | None
) -> (
    tuple[
        dict[int, etree._Element],
        dict[int, etree._Element],
        set[int],
        set[str],
        dict[str, set[int]],
    ]
    | None
):
    """The graph-derived members and hooks of one semantic family frame."""
    frame = _solo_frame_of(widget)
    if frame is None or localname(frame) != "SoloFrame":
        return None
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


def _hook_families(graph: ShowGraph, groups, toggles: dict[int, etree._Element]) -> set[str]:
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


def _state_owners(graph: ShowGraph, groups, states: set[int]) -> dict[str, set[int]]:
    families = (*FAMILIES, "pixel-mode")
    owners = {family: set() for family in families}
    for state_id in states:
        for function_id in _owner_frontier(graph, groups, state_id):
            for family in _owner_families(graph, groups, function_id):
                owners[family].add(function_id)
    return owners


def _owner_families(graph: ShowGraph, groups, function_id: int) -> tuple[str, ...]:
    """Every family a direct functional state owner can restore."""
    families = tuple(
        family
        for family, fixtures in _function_families(graph, groups, function_id).items()
        if fixtures
    )
    if graph.kind(function_id) in ("Chaser", "Sequence") and len(families) > 1:
        return ()
    return families


def _cached_state_owners(graph: ShowGraph, groups, states: set[int]) -> dict[str, set[int]]:
    state_ids = frozenset(states)
    if _OWNER_CACHE:
        cached_graph, cached_groups, cached_states, owners = _OWNER_CACHE[0]
        if cached_graph is graph and cached_groups is groups and cached_states == state_ids:
            return owners
    owners = _state_owners(graph, groups, states)
    _OWNER_CACHE[:] = [(graph, groups, state_ids, owners)]
    return owners


def _owner_frontier(graph: ShowGraph, groups, state_id: int) -> set[int]:
    """Functions whose starts can return one family to its room-state owner.

    A multi-family Chaser/Sequence coordinates structural level Collections;
    recurse through those until one family has its actual owner. A single-family
    Collection or Chaser such as `Movimientos Suaves` or `Gobo Animacion`
    remains the functional owner, never its leaf steps.
    """
    found: set[int] = set()
    for function_id in graph.members.get(state_id, ()):
        found.update(_nested_owner_frontier(graph, groups, function_id, False, set()))
    return found


def _nested_owner_frontier(
    graph: ShowGraph,
    groups,
    function_id: int,
    inside_structural_cycle: bool,
    seen: set[int],
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
    is_cycle = kind in ("Chaser", "Sequence") and len(families) > 1
    is_level = kind == "Collection" and inside_structural_cycle and len(families) > 1
    if not (is_cycle or is_level):
        return {function_id}
    nested_seen = {*seen, function_id}
    found: set[int] = set()
    for member_id in graph.members.get(function_id, ()):
        found.update(_nested_owner_frontier(graph, groups, member_id, True, nested_seen))
    return found


def _function_families(graph: ShowGraph, groups, function_id: int) -> dict[str, set[int]]:
    found = {family: set() for family in FAMILIES}
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


def _is_pixel_fixture(capability) -> bool:
    moving_roles = FAMILIES["position"]
    return (
        not capability.is_smoke
        and bool(capability.roles & FAMILIES["color"])
        and not bool(capability.roles & moving_roles)
        and roles.EFFECT in capability.roles
    )


def _sets_pixel_mode(capability, written: dict[int, int | None]) -> bool:
    return _is_pixel_fixture(capability) and any(
        capability.roles_by_offset[offset] == roles.EFFECT for offset in written
    )


def _solo_frame_of(widget: etree._Element | None) -> etree._Element | None:
    current = widget
    while current is not None:
        if localname(current) == "SoloFrame":
            return current
        current = current.getparent()
    return None
