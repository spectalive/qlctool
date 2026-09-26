"""The heads `Alternado` runs backwards: every other rigged head across the stage.

"Cada cabeza para un lado" (owner, 2026-09-22) is each head against its
neighbour, and a neighbour is the head beside it on the truss, so the order is
the stage's (`stage_ordered`), never the patch's. On Vibra the patch put the
7R beams at x 1916, 9694, 4405, 7205 mm, and every other of those was exactly
the house-right pair the default reverses: the seven `Alternado` buttons were
the plain ones again (en-sala DMX audit, 2026-09-26).

With two rigged heads, every other head *is* the house-right one, so reversal
cannot tell the two buttons apart. Ruling D5 (2026-09-26): both run forward
and the phase spread puts them half a figure apart - a true opposition. A lone
head the default runs forward is reversed instead, the one difference left.
"""

from collections.abc import Collection, Sequence

from ..every_other import every_other


def alternate_mirror(stage_rigged: Sequence[int], mirrored: Collection[int]) -> set[int]:
    """The reversed heads of `stage_rigged` (left to right), unlike the default `mirrored`."""
    default = set(mirrored) & set(stage_rigged)
    alternate = set(every_other(stage_rigged))
    if alternate != default:
        return alternate
    if default:
        return set()
    return set(stage_rigged)
