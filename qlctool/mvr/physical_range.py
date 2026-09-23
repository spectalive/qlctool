"""The physical span of a whole-range attribute: pan and tilt travel, zoom.

Values come from `<Physical>` where QLC+ states them and from GDTF's own
conventions where it does not: a mover with no stated travel gets 540/270, a
zoom with no stated spread gets a plausible one around what it does state.
"""

from ..definition import FixtureDefinition

DEFAULT_PAN, DEFAULT_TILT = 540.0, 270.0
DEFAULT_STROBE_HZ = (1.0, 20.0)


def physical_range(attribute: str, definition: FixtureDefinition) -> tuple[float, float]:
    optics = definition.optics
    if attribute == "Pan":
        travel = optics.pan_max if optics and optics.pan_max else DEFAULT_PAN
        return -travel / 2, travel / 2
    if attribute == "Tilt":
        travel = optics.tilt_max if optics and optics.tilt_max else DEFAULT_TILT
        return -travel / 2, travel / 2
    if attribute == "Zoom":
        narrow = optics.degrees_min if optics else 0.0
        wide = optics.degrees_max if optics else 0.0
        if not wide:
            return (narrow or 5.0), (narrow * 3 if narrow else 50.0)
        if wide == narrow:
            return narrow * 0.5, wide * 1.5
        return narrow, wide
    return 0.0, 1.0
