"""How many taps of the beat one layer is worth, as a QLC+ speed multiplier.

A tap dial's time is one tap - one beat. Every function under it then runs at
`beat x multiplier`, so the multiplier is that layer's length written in beats.
QLC+ only offers powers of two from a sixteenth to sixteen, so a layer built
for 3300 ms at a 500 ms beat (6.6 beats) becomes eight, not six: the nearest
rung, chosen on the logarithmic scale the rungs actually sit on.
"""

from math import log2

from .speed_dial import MULTIPLIERS

RUNGS = sorted(MULTIPLIERS)


def beat_multiplier(duration_ms: int, beat_ms: int) -> int:
    """The multiplier whose beat count sits nearest `duration_ms`."""
    if duration_ms <= 0 or beat_ms <= 0:
        return MULTIPLIERS[1]
    wanted = duration_ms / beat_ms
    nearest = min(RUNGS, key=lambda rung: abs(log2(rung) - log2(wanted)))
    return MULTIPLIERS[nearest]
