"""A 3x3 rotation about the Z axis, degrees, right-handed."""

import math


def rotation_about_z(degrees: float) -> list[list[float]]:
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]
