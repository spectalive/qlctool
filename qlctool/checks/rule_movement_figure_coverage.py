"""A movement figure that moves half the heads and leaves the others standing.

A figure on the JUGAR page is a Collection of the per-family EFX that draw it:
the washes' version and the beams' version under one name, because a wash's wide
soft beam and a 7R needle cannot share one geometry. The families are defined
shape by shape, so a shape one family never defined simply did not appear in the
Collection - and the button moved the six washes while the four beams stood
still, with nothing in the file saying anything was missing: "algunos
movimientos de cabeza no incluyen las beam" (owner, 2026-09-22).

The claim is read per fixture group, as `rule_wheel_colour` and
`rule_colour_animation_wheel` read theirs: the beams are *in* Cabezas beside the
washes, so a figure that moves that group has made a claim about all of it.

The question is asked of a console button, not of the functions under it. The
per-family pieces are *meant* to move one family - `Wash Rapido Circulo` is the
washes' circle and nothing else - and they are stacked into one button precisely
so that the room moves as a whole. So what has to cover the group is whatever the
operator can press: if pressing it animates part of Cabezas and leaves the rest
of Cabezas standing, the room shows half a rig moving.

Only EFX count. A Scene that aims the heads somewhere (`Beams Abanico`, the fan)
states positions rather than animating them, and asking a rest position to cover
both families would be asking for a different look.
"""

from lxml import etree

from .. import roles
from ..xmlutil import find_local, iter_local
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE_ID = "movement_figure_coverage"
EFX_PANTILT_MODE = "0"  # EFXFixture::Mode - PanTilt, Dimmer, RGB


def check_movement_figure_coverage(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, caption in sorted(entries.items()):
        moved = _moved_fixtures(graph, groups, function_id)
        if not moved:
            continue
        still = sorted(
            graph.capabilities[fixture_id].fixture.name
            for group_members in groups.values()
            if moved & set(group_members)
            for fixture_id in group_members
            if fixture_id not in moved and _can_move(graph, fixture_id)
        )
        if not still:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=caption,
                fixtures=tuple(still),
                message_id="movement_figure_still_heads",
                fields={
                    "moved": len(moved),
                    "still": len(still),
                },
            )
        )
    return findings


def _moves_pan_tilt(function: etree._Element) -> bool:
    """An EFX running any of its fixtures in PanTilt mode."""
    # An EFX names its members `<Fixture>`, not `<EFXFixture>` (efxfixture.cpp).
    for fixture in iter_local(function, "Fixture"):
        mode = find_local(fixture, "Mode")
        if mode is not None and (mode.text or "").strip() == EFX_PANTILT_MODE:
            return True
    return False


def _moved_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> set[int]:
    """The fixtures whose pan or tilt this button animates through an EFX."""
    moved: set[int] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or not _moves_pan_tilt(function):
            continue
        for fixture_id, pairs in driven_channels(function, graph.capabilities, groups).items():
            if _writes_pan_or_tilt(graph, fixture_id, pairs):
                moved.add(fixture_id)
    return moved


def _writes_pan_or_tilt(graph: ShowGraph, fixture_id: int, pairs: dict[int, int | None]) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None:
        return False
    return any(
        offset in pairs
        for role in (roles.PAN, roles.TILT)
        for offset in capability.offsets_for_role(role)
    )


def _can_move(graph: ShowGraph, fixture_id: int) -> bool:
    capability = graph.capabilities.get(fixture_id)
    return (
        capability is not None
        and capability.has_role(roles.PAN)
        and capability.has_role(roles.TILT)
    )
