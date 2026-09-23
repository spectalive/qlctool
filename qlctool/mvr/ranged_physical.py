"""The physical span of one ranged function: strobe Hz from `Res1`/`Res2`,
wheel spin in rpm, a shutter's open-or-closed.
"""

from ..definition import Capability
from .physical_range import DEFAULT_STROBE_HZ
from .set_physical import set_physical


def ranged_physical(target: str, capability: Capability) -> tuple[float, float]:
    if target in ("Shutter1Strobe", "Shutter1StrobePulse", "Shutter1StrobeRandom"):
        try:
            return float(capability.resource), float(capability.resource2)
        except ValueError:
            return DEFAULT_STROBE_HZ
    if target in ("Color1WheelSpin", "Gobo1WheelSpin"):
        return -60.0, 60.0
    if target == "Shutter1":
        physical = set_physical(target, capability)
        return physical, physical
    return 0.0, 1.0
