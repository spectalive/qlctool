"""A family of fixtures in the order the room sees them: rigged left to right, then spares.

Every other head, a phase spread and a serial wave are all orders, and the only
order the room can see is the one across the stage. Patch order is the order
somebody plugged the cables in: on Vibra it put the 7R beams at x 1916, 9694,
4405, 7205, so "every other" reversed exactly the house-right pair and
`Alternado` was the default under another name (en-sala DMX audit,
2026-09-26).

A spare in a flight case (`rigged_fixture_ids`) still gets its place - after
every rigged head, in the order given - so it can never take a slot a visible
head should have. A rigged fixture the plot has not placed keeps its given
order after the placed ones.
"""

from collections.abc import Sequence

from lxml import etree

from .rigged_fixture_ids import rigged_fixture_ids
from .stage_x_positions import stage_x_positions


def stage_ordered(root: etree._Element, fixture_ids: Sequence[int]) -> list[int]:
    """`fixture_ids` rigged by stage x first, then the spares in their given order."""
    rigged = rigged_fixture_ids(root)
    positions = stage_x_positions(root)
    placed = sorted(
        (fixture_id for fixture_id in fixture_ids if fixture_id in rigged),
        key=lambda fixture_id: (fixture_id not in positions, positions.get(fixture_id, 0.0)),
    )
    return placed + [fixture_id for fixture_id in fixture_ids if fixture_id not in rigged]
