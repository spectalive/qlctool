"""How far apart two colours sit on the colour wheel, in degrees, 0 to 180.

Complementary colours are 180 apart, a triad 120, neighbours 60 or less. The
hue is HSV's, so it is blind to how bright or how pale a colour is - red and
pastel red are 0 apart, which is what a rule about which hues mix wants.
"""

from .hue_degrees import hue_degrees
from .hue_gap import hue_gap

RGB = tuple[int, int, int]


def hue_distance(first: RGB, second: RGB) -> float:
    return hue_gap(hue_degrees(first), hue_degrees(second))
