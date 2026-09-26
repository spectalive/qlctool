"""Two movement buttons of one frame that the room cannot tell apart.

2026-09-26, en-sala DMX audit (item 2): the seven `Alternado` buttons moved the
four 7R beams and the two MAC WASH exactly as the seven plain buttons did.
"Every other head" was taken in patch order, and on this rig the beams at odd
patch positions are the house-right pair the default already reverses; the
washes' list was mostly spares, so the two rigged MACs landed on the same
direction and phase in both. The buttons differed only on fixtures in a flight
case.

A SoloFrame offers a choice. When two of its buttons start movement that is
identical on every rigged head - the same figures, sizes, centres, speeds,
propagation, and per head the same direction and start offset - the choice is
not there. Read off the EFX the buttons reach, never off their names.
"""

from lxml import etree

from ..rigged_fixture_ids import rigged_fixture_ids
from ..xmlutil import find_local, iter_local
from .finding import WARNING, Finding
from .movement_figure import MovementFigure
from .movement_signature import movement_signature
from .show_graph import ShowGraph
from .solo_frame_function_ids import solo_frame_function_ids

RULE_ID = "twin_movement"


def check_twin_movement(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    """Warn on every button of a SoloFrame that moves the rig like an earlier one."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    rigged = rigged_fixture_ids(root)
    findings: list[Finding] = []
    for frame in iter_local(console, "SoloFrame"):
        first: dict[frozenset[MovementFigure], int] = {}
        for function_id in solo_frame_function_ids(frame):
            signature = movement_signature(graph, function_id, rigged)
            if not signature:
                continue
            twin = first.setdefault(signature, function_id)
            if twin == function_id:
                continue
            heads = {head[0] for _, figure_heads in signature for head in figure_heads}
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=WARNING,
                    function=graph.name(function_id),
                    message_id="twin_movement_same",
                    fields={"twin": graph.name(twin)},
                    fixtures=tuple(
                        sorted(
                            graph.capabilities[head].fixture.name
                            for head in heads
                            if head in graph.capabilities
                        )
                    ),
                )
            )
    return findings
