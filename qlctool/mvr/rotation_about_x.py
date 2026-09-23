"""A 3x3 rotation about the X axis, degrees, right-handed."""

import math


def rotation_about_x(degrees: float) -> list[list[float]]:
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return [[1, 0, 0], [0, c, -s], [0, s, c]]
