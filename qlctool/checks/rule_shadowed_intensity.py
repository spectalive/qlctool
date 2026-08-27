"""A dimmer level that can never be seen, because a higher one runs beside it.

Intensity mixes HTP: of every function writing a dimmer channel, the highest
value wins. That is what made "Ambiente = dimmer bajo" impossible as first
planned (Codex review, 2026-08-27): the colour wheel ran the whole night with
every dimmer at 255, so a quiet level asking for 110 on the same channels
changed nothing - the room simply never dimmed, and nothing looked broken.

The shape of the bug is two *concurrent* branches of one Collection writing
the same dimmer channel to different definite values. Steps of one chaser are
alternatives and never fight; two members of a Collection run at the same
instant, and the lower value is dead code the room will never show. Colour
channels are deliberately out of scope - two colours on one fixture is the
`colores pisados` rule.
"""

from .. import roles
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "intensidad tapada"
LEAVES = ("Scene", "Sequence")


def check_shadowed_intensity(
    graph: ShowGraph, groups, entries
) -> list[Finding]:
    del groups
    findings: list[Finding] = []
    reported: set[tuple[int, int, int]] = set()
    for entry_id in sorted(entries):
        for collection_id in graph.collections(entry_id):
            findings += _collection(graph, collection_id, reported)
    return findings


def _collection(
    graph: ShowGraph, collection_id: int, reported
) -> list[Finding]:
    members = graph.members.get(collection_id, ())
    if len(members) < 2:
        return []
    writes = {member: _dimmer_writes(graph, member) for member in members}

    # channel -> the highest definite value any member writes, and who wrote it.
    highest: dict[tuple[int, int], tuple[int, int]] = {}
    for member, channels in writes.items():
        for channel, values in channels.items():
            value = max(values)
            if channel not in highest or value > highest[channel][0]:
                highest[channel] = (value, member)

    findings: list[Finding] = []
    for member, channels in writes.items():
        for channel, values in channels.items():
            top_value, top_member = highest[channel]
            low = min(values)
            if top_member == member or low >= top_value:
                continue
            key = (collection_id, member, top_member)
            if key in reported:
                continue
            reported.add(key)
            fixture = graph.capabilities.get(channel[0])
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(collection_id),
                message=(
                    f"«{graph.name(member)}» deja un dimmer a {low} mientras "
                    f"«{graph.name(top_member)}» tiene el mismo canal a "
                    f"{top_value} a la vez: la intensidad mezcla HTP, gana el "
                    f"alto y la bajada no se ve nunca"
                ),
                fixtures=(fixture.fixture.name,) if fixture is not None else (),
            ))
    return findings


def _dimmer_writes(
    graph: ShowGraph, function_id: int
) -> dict[tuple[int, int], set[int]]:
    """(fixture, offset) -> definite dimmer values the member's scenes state.

    Only Scenes: an EFX in dimmer mode writes values nobody can predict, and a
    matrix never touches a dimmer at all. Zeroes are skipped - a member turning
    a fixture off is not a second opinion about how bright it should be.
    """
    from .driven_channels import driven_channels

    writes: dict[tuple[int, int], set[int]] = {}
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or function.attrib.get("Type") not in LEAVES:
            continue
        for fixture_id, pairs in driven_channels(
            function, graph.capabilities, {}
        ).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or capability.is_smoke:
                continue
            dimmers = set(capability.offsets_for_role(roles.DIMMER))
            for offset, value in pairs.items():
                if offset in dimmers and value is not None and value > 0:
                    writes.setdefault((fixture_id, offset), set()).add(value)
    return writes
