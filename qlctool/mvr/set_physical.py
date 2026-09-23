"""The physical value of one channel set: 0 for a closed shutter or a prism
out of the beam, 1 for open or in, from the preset or the range's name.
"""

from ..definition import Capability


def set_physical(target: str, capability: Capability) -> float:
    if target == "Shutter1":
        closed = capability.preset == "ShutterClose" or any(
            word in capability.name.lower() for word in ("closed", "blackout", "close")
        )
        return 0.0 if closed else 1.0
    if target == "Prism1":
        return (
            0.0
            if capability.preset == "PrismEffectOff"
            or "off" in capability.name.lower()
            or "none" in capability.name.lower()
            else 1.0
        )
    return 0.0
