"""Whether a function opens a fixture's intensity path: its dimmer or its shutter."""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from ..shutter_open_ranges import shutter_open_ranges
from ..wheel_blade_offsets import wheel_blade_offsets


def touches_intensity_path(capability: FixtureCapabilities, written: dict[int, int | None]) -> bool:
    # A wheel-only head's blade opens with its colour (ruling D8, 2026-09-27):
    # a colour look writing it states colour, not the intensity of the rig.
    blades = set(wheel_blade_offsets(capability))
    dimmers = [o for o in capability.offsets_for_role(roles.DIMMER) if o not in blades]
    if any(offset in written for offset in dimmers):
        return True
    return any(offset in written for offset, _ in shutter_open_ranges(capability))
