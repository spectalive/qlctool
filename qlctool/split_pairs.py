"""What a per-group mix wheel steps: neighbours both ways round, plus the show's keys.

Every ordered pair of six colours used to be here, thirty per group, white
included - "Azul / Amarillo" on alternate PARs of one truss, which mix towards
white where their pools meet. Since 2026-09-22 a split inside one group is
neighbours only (`analogous_pairs`, both ways round so the odd and the even
fixtures swap), plus the two key pairs the owner's hand knows (a triad the
rule tolerates). `rule_split_complementary` sees anything else.
"""

from .analogous_pairs import ANALOGOUS_PAIRS
from .key_split_pairs import KEY_SPLIT_PAIRS

SPLIT_PAIRS: tuple[tuple[str, str], ...] = tuple(
    dict.fromkeys(
        [
            *((pair.lead, pair.bed) for pair in ANALOGOUS_PAIRS),
            *((pair.bed, pair.lead) for pair in ANALOGOUS_PAIRS),
            *KEY_SPLIT_PAIRS,
        ]
    )
)
