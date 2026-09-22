"""A colour's hue on the wheel, 0 to 360, blind to how bright or how pale it is."""

import colorsys

RGB = tuple[int, int, int]
FULL = 255
TURN = 360.0


def hue_degrees(rgb: RGB) -> float:
    hue, _, _ = colorsys.rgb_to_hsv(*(value / FULL for value in rgb))
    return hue * TURN
