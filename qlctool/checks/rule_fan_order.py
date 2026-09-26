"""A fan of heads that folds back on itself across the stage.

2026-09-27, Round 2 review of the en-sala DMX audit: `Beams Abanico` spread
the four 7R evenly over the audience window - 62, 75, 89, 102 - but in patch
order. Across the stage (x 1916, 4405, 7205, 9694 mm: fixtures 20, 22, 23, 21)
that read 62, 89, 102, 75, and the house-right head folded back into the
middle. `Beams Cruce`, the fan reversed, broke the same way. The same cause as
the `Alternado` buttons (`twin_movement`): patch order taken for stage order.

A Scene whose pans on three or more rigged heads of one family are evenly
spaced is a fan, whatever it is called (`is_even_spread`), and a fan is only
a fan if the pans rise, or fall, head by head across the stage. A look aimed
by hand - two heads on one pan, uneven gaps - is left alone. Read off the
values, the capabilities and the stage plot, never off names.
"""

from lxml import etree

from ..rigged_fixture_ids import rigged_fixture_ids
from ..stage_x_positions import stage_x_positions
from .finding import WARNING, Finding
from .is_even_spread import is_even_spread
from .is_monotonic import is_monotonic
from .show_graph import ShowGraph
from .stage_pan_rows import stage_pan_rows

RULE_ID = "fan_order"


def check_fan_order(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element
) -> list[Finding]:
    """Warn on every Scene that fans a family's rigged heads out of stage order."""
    rigged = rigged_fixture_ids(root)
    positions = stage_x_positions(root)
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        if graph.functions[function_id].attrib.get("Type") != "Scene":
            continue
        for row in stage_pan_rows(graph, groups, function_id, rigged, positions):
            pans = [pan for _, pan in row]
            if not is_even_spread(pans) or is_monotonic(pans):
                continue
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=WARNING,
                    function=graph.name(function_id),
                    message_id="fan_order_folded",
                    fields={"count": len(row), "pans": ", ".join(str(pan) for pan in pans)},
                    fixtures=tuple(graph.capabilities[i].fixture.name for i, _ in row),
                )
            )
    return findings
