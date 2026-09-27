"""How far an EFX figure reaches from its centre, per axis, once QLC+ turns it.

A figure's size is not its reach. QLC+ scales the unit shape and turns it in
one step - `EFX::rotateAndScale` in `engine/src/efx.cpp` (lines 306-327):

    pan  = XOffset + x*cosR*Width + y*sinR*Height
    tilt = YOffset - x*sinR*Width + y*cosR*Height

so a Diamond of Width 20 and Height 13 turned 90 degrees swings tilt by 20,
not 13. Judging `offset +- Height` was right only at Rotation 0, and every
Diamante on the 7R left the audience window about 30% of the time (en-sala
DMX re-audit, 2026-09-27). The reach is read by sampling the unit shape
(`efx_unit_point`) over the whole turn and pushing each point through that
formula; the fade-in scale QLC+ also applies only ever shrinks the figure.
"""

import math

from .efx_unit_point import efx_unit_point


def efx_extent(
    algorithm: str,
    width: float,
    height: float,
    rotation: float,
    x_frequency: float = 2,
    y_frequency: float = 3,
    x_phase: float = math.pi / 2,
    y_phase: float = 0.0,
    steps: int = 720,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """((pan_min, pan_max), (tilt_min, tilt_max)) as offsets from the centre.

    `rotation` is in degrees, as `<Rotation>` stores it; the phases are in
    radians, as `efx_unit_point` takes them.
    """
    radians = math.pi / 180 * rotation
    cos_r = math.cos(radians)
    sin_r = math.sin(radians)
    pans: list[float] = []
    tilts: list[float] = []
    for step in range(steps):
        x, y = efx_unit_point(
            algorithm, math.pi * 2 * step / steps, x_frequency, y_frequency, x_phase, y_phase
        )
        pans.append(x * cos_r * width + y * sin_r * height)
        tilts.append(-x * sin_r * width + y * cos_r * height)
    return (min(pans), max(pans)), (min(tilts), max(tilts))
