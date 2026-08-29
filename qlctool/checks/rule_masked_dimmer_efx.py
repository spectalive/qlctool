"""A dimmer effect that can never be seen, because a full scene runs beside it.

Intensity mixes HTP and an EFX cannot write above 255: a Scene holding a dimmer
channel at 255 while an EFX drives the same channel makes every dip the effect
draws invisible - the room shows a flat wall of light and the effect is
cosmetic forever. That is what "modo locura empieza todo blanco y normal"
turned out to be (owner, 2026-08-29): `Momento Locura` carried `Intensidad
Total` beside `Dimmer Chase`, the exact pairing the levels had already learned
to avoid with a dimmerless base.

`intensidad tapada` cannot see this on purpose - it compares definite values
and an EFX never states one. But 255 needs no prediction: nothing the effect
writes can ever exceed it, so the masking is certain, not probable.

The shape is two *concurrent* branches of one Collection: one reaching a Scene
that states 255 on a dimmer channel, the other reaching an EFX in Dimmer mode
on the same channel. Steps of one chaser are alternatives and never fight.
"""

from .. import roles
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "efx de dimmer tapado"
FULL = 255


def check_masked_dimmer_efx(
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
    efx_channels = {member: _efx_dimmers(graph, member) for member in members}
    full_channels = {member: _full_writes(graph, member) for member in members}

    findings: list[Finding] = []
    for efx_member, driven in efx_channels.items():
        for full_member, held in full_channels.items():
            if efx_member == full_member:
                continue
            masked = driven & held
            if not masked:
                continue
            key = (collection_id, efx_member, full_member)
            if key in reported:
                continue
            reported.add(key)
            names = sorted({
                graph.capabilities[fixture].fixture.name
                for fixture, _ in masked
                if fixture in graph.capabilities
            })
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(collection_id),
                message=(
                    f"«{graph.name(full_member)}» clava un dimmer a {FULL} "
                    f"mientras «{graph.name(efx_member)}» lo mueve como "
                    f"efecto a la vez: la intensidad mezcla HTP, nada supera "
                    f"{FULL} y el efecto no se ve nunca"
                ),
                fixtures=tuple(names),
            ))
    return findings


def _efx_dimmers(graph: ShowGraph, function_id: int) -> set[tuple[int, int]]:
    """(fixture, offset) dimmer channels an EFX under this branch drives."""
    channels: set[tuple[int, int]] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or function.attrib.get("Type") != "EFX":
            continue
        for fixture_id, pairs in driven_channels(
            function, graph.capabilities, {}
        ).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or capability.is_smoke:
                continue
            dimmers = set(capability.offsets_for_role(roles.DIMMER))
            channels |= {
                (fixture_id, offset) for offset in pairs if offset in dimmers
            }
    return channels


def _full_writes(graph: ShowGraph, function_id: int) -> set[tuple[int, int]]:
    """(fixture, offset) dimmer channels a Scene under this branch holds at 255."""
    channels: set[tuple[int, int]] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or function.attrib.get("Type") not in (
            "Scene", "Sequence"
        ):
            continue
        for fixture_id, pairs in driven_channels(
            function, graph.capabilities, {}
        ).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or capability.is_smoke:
                continue
            dimmers = set(capability.offsets_for_role(roles.DIMMER))
            channels |= {
                (fixture_id, offset)
                for offset, value in pairs.items()
                if offset in dimmers and value == FULL
            }
    return channels
