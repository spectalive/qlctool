"""The range of a shutter channel that actually strobes, if it has one.

Preset first and name only as a fallback: reading the name alone picks
"No strobe" out of a channel that labels its open position that way - which is
how a split CLB2.4 came out with `Strobo ON` sending 0, the one value that
guarantees no strobe at all. A preset is what the definition means; a name is
what it happens to say.
"""

from .definition import Capability

# QLC+ names every strobing preset "Strobe..." - StrobeSlowToFast,
# StrobeFastToSlow, StrobeRandom..., and so on.
STROBE_PRESET_PREFIX = "Strobe"
SHUTTER_PRESETS = ("ShutterOpen", "ShutterClose")


def strobe_range(ranges: tuple[Capability, ...]) -> Capability | None:
    for capability in ranges:
        if (capability.preset or "").startswith(STROBE_PRESET_PREFIX):
            return capability
    for capability in ranges:
        if (capability.preset or "") in SHUTTER_PRESETS:
            continue
        if "strobe" in capability.name.lower() and "no strobe" not in capability.name.lower():
            return capability
    return None
