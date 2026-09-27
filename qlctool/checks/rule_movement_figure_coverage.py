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

Only rigged heads are owed a figure. A spare the stage plot hides in a flight
case moves for nobody, and asking the waves to carry the spares put six
invisible heads into `Ola Vertical Washes`' propagation, so the two rigged MACs
were a ninth of a loop apart instead of a third (Round 2 review of the en-sala
DMX audit, 2026-09-27).

Only EFX count. A Scene that aims the heads somewhere (`Beams Abanico`, the fan)
states positions rather than animating them, and asking a rest position to cover
both families would be asking for a different look.
"""

from lxml import etree

from ..rigged_fixture_ids import rigged_fixture_ids
from .finding import ERROR, Finding
from .fixture_can_move import fixture_can_move
from .pan_tilt_moved_fixtures import pan_tilt_moved_fixtures
from .show_graph import ShowGraph

RULE_ID = "movement_figure_coverage"


def check_movement_figure_coverage(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    entries: dict[int, str],
    root: etree._Element,
) -> list[Finding]:
    rigged = rigged_fixture_ids(root)
    findings: list[Finding] = []
    for function_id, caption in sorted(entries.items()):
        moved = pan_tilt_moved_fixtures(graph, groups, function_id)
        if not moved:
            continue
        still = sorted(
            graph.capabilities[fixture_id].fixture.name
            for group_members in groups.values()
            if moved & set(group_members)
            for fixture_id in group_members
            if fixture_id not in moved
            and fixture_id in rigged
            and fixture_can_move(graph, fixture_id)
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
                fields={"moved": len(moved), "still": len(still)},
            )
        )
    return findings
