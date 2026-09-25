"""Whether a deal shows one group exactly two opposite hues in some rotation."""

from collections.abc import Sequence

from ..argb import RGB
from ..complementary_from import COMPLEMENTARY_FROM
from ..hue_distance import hue_distance


def opposite_split(seats: Sequence[int], colours: Sequence[RGB]) -> bool:
    """True when some rotation of `colours` over these seats gives exactly two
    distinct colours `COMPLEMENTARY_FROM` or more apart - what
    `rule_split_complementary` reports.
    """
    count = len(colours)
    for offset in range(count):
        shown = sorted({colours[(seat + offset) % count] for seat in seats})
        if len(shown) == 2 and hue_distance(shown[0], shown[1]) >= COMPLEMENTARY_FROM:
            return True
    return False
