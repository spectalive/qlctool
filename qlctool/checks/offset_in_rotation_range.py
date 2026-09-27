"""Whether a value on this offset lands in a labelled rotation range."""

from ..fixture_capabilities import FixtureCapabilities

ROTATION = "Rotation"


def offset_in_rotation_range(capability: FixtureCapabilities, offset: int, value: int) -> bool:
    for ranges in [capability.capabilities_by_offset[offset]]:
        for entry in ranges:
            if entry.minimum <= value <= entry.maximum and entry.preset.startswith(ROTATION):
                return True
    return False
