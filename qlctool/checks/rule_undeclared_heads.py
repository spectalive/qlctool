"""A fixture with several sets of colour channels that declares only one head.

A matrix does not paint fixtures, it paints the **cells** of a fixture group,
and a cell holds one *head*. Which channels a head owns comes from the
definition's `<Head>` blocks - and when a mode declares none, QLC+ does not
treat the fixture as headless: it builds one head holding every channel
(`Fixture::loadXML`, engine/src/fixture.cpp:686). That head then caches one
channel per colour, and `QLCFixtureHead::cacheChannels` overwrites as it walks
the mode, so the **last** red wins.

So a fixture with three RGB rings and no `<Head>` offers a matrix exactly one
ring - the outer one - and leaves the other two holding whatever was written
last. It is the panels' bug wearing a different coat: everything looks patched,
the colour bank works (a scene writes every offset it finds), and only the
matrix comes out wrong, on part of a fixture, which is the hardest kind of wrong
to see from the desk.

Found on the two MAC WASH 1915Z when they were about to be grouped
(2026-08-31): 23-channel mode, `Red/Green/Blue ring 1..3`, no heads declared.
The fix is in the definition, not the show - three `<Head>` blocks, one per
ring, exactly as the CLB2.4 and the LED bars already have.

The rule only asks it of fixtures that are in a group, because a group is what
a matrix paints; an ungrouped fixture has no cells and nothing to get wrong.

It counts the heads that actually *hold* a red, a green and a blue, not the
`<Head>` elements. Three empty blocks, or three that list the pan and tilt
channels, satisfy a count and leave the matrix exactly as broken as before.
"""

from lxml import etree

from .. import roles
from ..fixture_group import fixture_groups
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "cabezas sin declarar"
COLOUR_ROLES = (roles.RED, roles.GREEN, roles.BLUE)


def check_undeclared_heads(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    findings: list[Finding] = []
    grouped = {
        fixture_id: group.name for group in fixture_groups(root) for fixture_id in group.fixture_ids
    }
    for fixture_id, group_name in sorted(grouped.items()):
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        sets = min(len(capability.offsets_for_role(role)) for role in COLOUR_ROLES)
        if sets < 2:
            continue
        declared = _colour_heads(capability)
        if declared >= sets:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=group_name,
                message=(
                    f"la definicion le da {sets} juegos de RGB y solo {declared} "
                    f"<Head> con rojo, verde y azul dentro: QLC+ fabrica una sola "
                    f"cabeza y se queda "
                    f"con el ultimo rojo, verde y azul, asi que una matriz sobre "
                    f"«{group_name}» solo pinta uno de los juegos y los demas se "
                    f"quedan con lo ultimo que alguien escribio"
                ),
                fixtures=(capability.fixture.name,),
            )
        )
    return findings


def _colour_heads(capability) -> int:
    """How many declared heads carry a full RGB set of their own."""
    by_role = {role: set(capability.offsets_for_role(role)) for role in COLOUR_ROLES}
    return sum(
        1
        for head in capability.declared_heads
        if all(by_role[role] & set(head) for role in COLOUR_ROLES)
    )
