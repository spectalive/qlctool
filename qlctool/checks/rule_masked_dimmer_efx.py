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

from .finding import ERROR, Finding
from .full_dimmer_writes import FULL
from .masked_collection_pairs import masked_collection_pairs
from .show_graph import ShowGraph

RULE_ID = "masked_dimmer_efx"


def check_masked_dimmer_efx(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    del groups
    findings: list[Finding] = []
    reported: set[tuple[int, int, int]] = set()
    for entry_id in sorted(entries):
        for collection_id in graph.collections(entry_id):
            for efx_member, full_member, names in masked_collection_pairs(
                graph, collection_id, reported
            ):
                findings.append(
                    Finding(
                        rule_id=RULE_ID,
                        severity=ERROR,
                        function=graph.name(collection_id),
                        message_id="masked_dimmer_efx_hidden",
                        fields={
                            "full": graph.name(full_member),
                            "level": FULL,
                            "efx": graph.name(efx_member),
                        },
                        fixtures=names,
                    )
                )
    return findings
