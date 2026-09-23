"""The GDTF attribute one labelled range of a channel stands for.

A QLC+ shutter channel is closed here, open there and a strobe in between; a
wheel channel holds its slots and then spins. GDTF says the same thing with one
ChannelFunction per stretch, each under its own attribute, and BlenderDMX
decides from that attribute whether the beam is off, on or flashing and whether
a wheel is indexed or rotating. This reads the capability preset, the precise
statement, before falling back to the range's name.
"""

from ..definition import Capability

_ROTATION = "Rotation"


def gdtf_range_attribute(attribute: str, capability: Capability) -> str:
    """The attribute for this range of a channel whose own attribute is given."""
    preset = capability.preset
    name = capability.name.lower()
    if attribute == "Shutter1":
        if preset.startswith("Pulse") or "pulse" in name:
            return "Shutter1StrobePulse"
        if preset.startswith("StrobeRandom") or "random" in name:
            return "Shutter1StrobeRandom"
        if preset.startswith("Strobe") or (not preset and "strob" in name):
            return "Shutter1Strobe"
        return "Shutter1"
    if attribute == "Color1":
        if preset.startswith(_ROTATION) or "rainbow" in name:
            return "Color1WheelSpin"
        if preset == "ColorWheelIndex":
            return "Color1WheelIndex"
        return "Color1"
    if attribute == "Gobo1":
        if preset.startswith(_ROTATION):
            return "Gobo1WheelSpin"
        if preset.startswith("GoboShake") or "shake" in name:
            return "Gobo1SelectShake"
        return "Gobo1"
    return attribute
