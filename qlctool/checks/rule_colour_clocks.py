"""Two colour clocks ticking in one room state.

The owner saw it in the preview before any rule did: "las barras led van con
los colores a su bola, no siguen el show" (2026-08-26). The rig-wide wheel was
stepping the room through cyan while the bars' own matrix cycle was stepping
the bars through magenta, and both were correct alone. Two chasers that each
rotate colour never agree, because nothing in QLC+ ties one chaser's step to
another's: the room reads as one show and a stray group doing a different one.

A *colour clock* is recognised by shape, never by name: a chaser at least two
of whose steps state different colours on RGB-capable fixtures - through the
scenes they reach, or through the colour an RGBMatrix paints its group. A
room *state* - AUTO, a moment - answers for the whole rig at once, so it gets
one clock at most. A manual layer is not judged here: pressing two colour
layers together is an operator's choice, a state is a promise.
"""

from lxml import etree

from .. import roles
from ..xmlutil import find_local, findall_local
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "relojes de color"

# One step's colour claim: hashable items a signature is made of.
Signature = frozenset


def check_colour_clocks(
    graph: ShowGraph, groups, entries: dict[int, str], states: set[int] | None = None
) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(states or ()):
        if function_id not in entries:
            continue
        for collection_id in sorted(graph.collections(function_id)):
            clocks: dict[int, set[int]] = {}
            for member in graph.members.get(collection_id, ()):
                found = _clocks_below(graph, groups, member)
                if found:
                    clocks[member] = found
            distinct = set().union(*clocks.values()) if clocks else set()
            if len(clocks) < 2 or len(distinct) < 2:
                continue
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(collection_id),
                message=(
                    "arranca a la vez "
                    + " y ".join(
                        f"«{graph.name(clock)}»" for clock in sorted(distinct)
                    )
                    + ", dos ciclos que rotan color cada uno a su ritmo: los "
                    f"fixtures de uno van a su bola respecto al resto "
                    f"(boton: {entries[function_id]})"
                ),
                fixtures=_stray_fixtures(graph, groups, distinct),
            ))
    return findings


def _clocks_below(graph: ShowGraph, groups, function_id: int) -> set[int]:
    """The colour clocks among this function and everything it starts."""
    return {
        member
        for member in graph.descendants(function_id)
        if graph.kind(member) == "Chaser"
        and _is_colour_clock(graph, groups, member)
    }


def _is_colour_clock(graph: ShowGraph, groups, chaser_id: int) -> bool:
    """At least two of the chaser's steps state different, non-dark colours."""
    stated: set[Signature] = set()
    for step in graph.members.get(chaser_id, ()):
        signature = _step_colours(graph, groups, step)
        if signature:
            stated.add(signature)
        if len(stated) >= 2:
            return True
    return False


def _step_colours(graph: ShowGraph, groups, step_id: int) -> Signature:
    """What colour this step puts where, over everything the step starts."""
    items: set[tuple] = set()
    for member in graph.descendants(step_id):
        function = graph.functions.get(member)
        if function is None:
            continue
        kind = function.attrib.get("Type")
        if kind in ("Scene", "Sequence"):
            items |= _scene_colours(graph, function)
        elif kind == "RGBMatrix":
            items |= _matrix_colours(graph, groups, function)
    return frozenset(items)


def _scene_colours(graph: ShowGraph, function: etree._Element) -> set[tuple]:
    items: set[tuple] = set()
    for fixture_id, pairs in driven_channels(
        function, graph.capabilities, {}
    ).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        rgb = {
            offset
            for role in (roles.RED, roles.GREEN, roles.BLUE)
            for offset in capability.offsets_for_role(role)
        }
        items |= {
            (fixture_id, offset, value)
            for offset, value in pairs.items()
            if offset in rgb and value
        }
    return items


def _matrix_colours(graph: ShowGraph, groups, function: etree._Element) -> set[tuple]:
    group = find_local(function, "FixtureGroup")
    colour = _matrix_colour(function)
    if group is None or not (group.text or "").isdigit() or colour is None:
        return set()
    return {
        (fixture_id, "matrix", colour)
        for fixture_id in groups.get(int(group.text), ())
        if (capability := graph.capabilities.get(fixture_id)) is not None
        and any(
            capability.has_role(role)
            for role in (roles.RED, roles.GREEN, roles.BLUE)
        )
    }


def _matrix_colour(function: etree._Element) -> int | None:
    """The ARGB an RGBMatrix paints with, in either colour format."""
    mono = find_local(function, "MonoColor")
    if mono is not None and (mono.text or "").isdigit():
        return int(mono.text)
    for colour in findall_local(function, "Color"):
        if colour.attrib.get("Index") == "0" and (colour.text or "").isdigit():
            return int(colour.text)
    return None


def _stray_fixtures(graph: ShowGraph, groups, clock_ids: set[int]) -> tuple[str, ...]:
    """The fixtures the narrower clocks paint: the group off on its own beat."""
    painted = {
        clock: {
            item[0]
            for step in graph.members.get(clock, ())
            for item in _step_colours(graph, groups, step)
        }
        for clock in clock_ids
    }
    widest = max(painted, key=lambda clock: len(painted[clock]))
    stray = set().union(
        *(fixtures for clock, fixtures in painted.items() if clock != widest)
    )
    return tuple(sorted(
        graph.capabilities[fixture_id].fixture.name
        for fixture_id in stray
        if fixture_id in graph.capabilities
    ))
