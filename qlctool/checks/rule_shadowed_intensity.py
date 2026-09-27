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

from .finding import ERROR, Finding
from .shadowed_collection_pairs import shadowed_collection_pairs
from .show_graph import ShowGraph

RULE_ID = "shadowed_intensity"


def check_shadowed_intensity(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    del groups
    findings: list[Finding] = []
    reported: set[tuple[int, int, int]] = set()
    for entry_id in sorted(entries):
        for collection_id in graph.collections(entry_id):
            for member, top_member, low, top_value, name in shadowed_collection_pairs(
                graph, collection_id, reported
            ):
                findings.append(
                    Finding(
                        rule_id=RULE_ID,
                        severity=ERROR,
                        function=graph.name(collection_id),
                        message_id="shadowed_intensity_hidden",
                        fields={
                            "member": graph.name(member),
                            "low": low,
                            "top": graph.name(top_member),
                            "top_value": top_value,
                        },
                        fixtures=(name,) if name is not None else (),
                    )
                )
    return findings
