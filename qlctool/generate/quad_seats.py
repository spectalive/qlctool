"""Where each fixture sits in the four-colour deal, so no pair of one group is opposite.

The deal walks its colours over the rig in patch order, one seat per fixture,
and each scene shifts every seat by one. A group of four or more takes all of
them; a group of two takes two neighbours of the cycle, and blue, red, green,
yellow ends on yellow beside blue: `Rig 4 Colores 4` put them on the two pars
of a small rig, and `check` reported `complementarios en un mismo lavado`
(2026-09-25). So a group with exactly two dealt members moves its second
member to the nearest seat whose colour stays less than
`COMPLEMENTARY_FROM` from the first's in every rotation: blue with green, red
with yellow. A group that already deals cleanly keeps its seats.
"""

from collections.abc import Iterable, Sequence

from ..argb import RGB
from ..checks.rule_split_complementary import COMPLEMENTARY_FROM
from ..hue_distance import hue_distance


def quad_seats(
    dealt_ids: Sequence[int],
    groups: Iterable[Sequence[int]],
    colours: Sequence[RGB],
) -> dict[int, int]:
    """Fixture id -> seat: its patch-order index, moved only for a clashing pair."""
    seats = {fixture_id: index for index, fixture_id in enumerate(dealt_ids)}
    count = len(colours)

    # The distances between two seats that never put opposite hues side by side.
    clean = [
        step
        for step in range(count)
        if all(
            hue_distance(colours[offset], colours[(offset + step) % count]) < COMPLEMENTARY_FROM
            for offset in range(count)
        )
    ]
    for members in groups:
        pair = [fixture_id for fixture_id in members if fixture_id in seats]
        if len(pair) != 2:
            continue
        first, second = pair
        if (seats[second] - seats[first]) % count in clean:
            continue
        step = next((step for step in clean if step), None)
        if step is not None:
            seats[second] = seats[first] + step
    return seats
