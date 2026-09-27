"""A beam's continuous half-colour channel, beside its colour wheel, if any."""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities


def multicolor_offset(beam: FixtureCapabilities) -> int | None:
    wheel = beam.wheel_for_role(roles.COLOR_MACRO)
    if wheel is None:
        return None
    wheel_offset, _ = wheel
    for offset in beam.offsets_for_role(roles.COLOR_MACRO):
        if offset == wheel_offset:
            continue
        ranges = beam.capabilities_by_offset[offset]
        if len(ranges) == 1 and ranges[0].minimum == 0 and ranges[0].maximum == 255:
            return offset
    return None
