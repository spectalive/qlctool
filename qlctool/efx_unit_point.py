"""The point an EFX algorithm draws at one moment, before QLC+ sizes and turns it.

A straight port of `EFX::calculatePoint(float iterator, float *x, float *y)`
in QLC+'s `engine/src/efx.cpp` (lines 378-490), up to - not including - its
closing `rotateAndScale`: each algorithm maps an iterator in 0..2*pi onto a
unit shape with x and y in -1..1. Width, height, rotation and the offsets are
applied afterwards (`efx_extent`), exactly as QLC+ applies them.

An algorithm QLC+ does not know falls back to Circle, the `default:` of the
switch - and of `EFX::stringToAlgorithm`.
"""

import math

from .efx_triangle_wave import efx_triangle_wave

_HALF_PI = math.pi / 2


def efx_unit_point(
    algorithm: str,
    iterator: float,
    x_frequency: float = 2,
    y_frequency: float = 3,
    x_phase: float = _HALF_PI,
    y_phase: float = 0.0,
) -> tuple[float, float]:
    """(x, y) of `algorithm` at `iterator` radians; phases are in radians.

    The frequencies and phases are the per-axis ones written under `<Axis>`
    and only Lissajous reads them; the defaults are QLC+'s constructor's.
    """
    if algorithm == "Eight":
        return math.cos(iterator * 2 + _HALF_PI), math.cos(iterator)
    if algorithm == "Line":
        return math.cos(iterator), math.cos(iterator)
    if algorithm == "Line2":
        return iterator / math.pi - 1, iterator / math.pi - 1
    if algorithm == "Diamond":
        return math.cos(iterator - _HALF_PI) ** 3, math.cos(iterator) ** 3
    if algorithm == "Square":
        if iterator < math.pi / 2:
            return (iterator * 2 / math.pi) * 2 - 1, 1.0
        if iterator < math.pi:
            return 1.0, (1 - (iterator - math.pi / 2) * 2 / math.pi) * 2 - 1
        if iterator < math.pi * 3 / 2:
            return (1 - (iterator - math.pi) * 2 / math.pi) * 2 - 1, -1.0
        return -1.0, ((iterator - math.pi * 3 / 2) * 2 / math.pi) * 2 - 1
    if algorithm == "SquareChoppy":
        return float(round(math.cos(iterator))), float(round(math.sin(iterator)))
    if algorithm == "SquareTrue":
        if iterator < math.pi / 2:
            return 1.0, 1.0
        if iterator < math.pi:
            return 1.0, -1.0
        if iterator < math.pi * 3 / 2:
            return -1.0, -1.0
        return -1.0, 1.0
    if algorithm == "Leaf":
        return math.cos(iterator + _HALF_PI) ** 5, math.cos(iterator)
    if algorithm == "Lissajous":
        x = (
            math.cos(x_frequency * iterator - x_phase)
            if x_frequency > 0
            else efx_triangle_wave(iterator, x_phase)
        )
        y = (
            math.cos(y_frequency * iterator - y_phase)
            if y_frequency > 0
            else efx_triangle_wave(iterator, y_phase)
        )
        return x, y
    return math.cos(iterator + _HALF_PI), math.cos(iterator)
