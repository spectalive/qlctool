"""Where each fixture sits in the four-colour deal, so no group is split in two opposites.

The deal walks its colours over the rig in patch order, one seat per fixture,
and each scene shifts every seat by one. A group of two takes two neighbours
of the cycle, and blue, red, green, yellow ends on yellow beside blue: `Rig 4
Colores 4` put them on the two pars of a small rig, and `check` reported
`complementarios en un mismo lavado` (2026-09-25). A larger group whose
members fall on opposite seats (patch indices 0, 3, 4, 7) is the same split
twice. So a group the deal would show exactly two opposite hues
(`opposite_split`) is re-dealt to an adjacent pair: its members alternate
between the first one's seat and the nearest seat whose colour stays under
`COMPLEMENTARY_FROM` from it in every rotation - blue with green, red with
yellow. Groups are visited in ascending id, so a fixture in two of them ends
where the last one puts it; a group the deal already suits keeps its seats.
"""

from collections.abc import Mapping, Sequence

from ..argb import RGB
from .opposite_split import opposite_split


def quad_seats(
    dealt_ids: Sequence[int],
    groups: Mapping[int, Sequence[int]],
    colours: Sequence[RGB],
) -> dict[int, int]:
    """Fixture id -> seat: its patch-order index, moved only in a group split in two opposites."""
    seats = {fixture_id: index for index, fixture_id in enumerate(dealt_ids)}
    # The nearest seat distance that never puts opposite hues side by side.
    step = next(
        (step for step in range(1, len(colours)) if not opposite_split((0, step), colours)), None
    )
    for _group_id, members in sorted(groups.items()):
        dealt = [fixture_id for fixture_id in members if fixture_id in seats]
        if step is None or not opposite_split([seats[m] for m in dealt], colours):
            continue
        first = seats[dealt[0]]
        for index, fixture_id in enumerate(dealt):
            seats[fixture_id] = first + (index % 2) * step
    return seats
