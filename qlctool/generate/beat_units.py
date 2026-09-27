"""Beats to QLC+'s thousandths, on its own eighth-of-a-beat grid."""

QUANTUM = 125
# QLC+ quantises a beat into eighths; 1000 units is one beat.
UNITS_PER_BEAT = 1000


def beat_units(beats: float) -> int:
    return round(beats * UNITS_PER_BEAT / QUANTUM) * QUANTUM
