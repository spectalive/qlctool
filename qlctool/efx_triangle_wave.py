"""The back-and-forth ramp QLC+ draws on a Lissajous axis whose frequency is 0.

Mirrors the `m_xFrequency > 0` / `m_yFrequency > 0` else-branches of
`EFX::calculatePoint(float iterator, ...)` in QLC+'s `engine/src/efx.cpp`
(lines 468-476 and 480-488): instead of a cosine the axis walks linearly from
-1 to 1 over one half-turn and back over the next, offset by the axis phase.
"""

import math


def efx_triangle_wave(iterator: float, phase: float) -> float:
    """The -1..1 value of the ramp at `iterator` radians, with `phase` in radians."""
    position = (iterator + phase) / math.pi
    whole = int(position)
    position -= whole - whole % 2
    forward = 1 - math.floor(position)
    backward = 1 - forward
    position = position - math.floor(position)
    return (forward * position + backward * (1 - position)) * 2 - 1
