"""Whether a held flash lights a fixture, read off its capabilities.

A fixture with a dimmer is lit by the dimmer, or by a labelled shutter opened
(`raises_light`). A fixture whose only intensity path is its shutter - the MiN
Wash has no dimmer channel at all - is lit by strobing that shutter: a flash
that drives it into a strobing value is the flash reaching it. A strobe on a
fixture that has a dimmer lights nothing by itself; it chops whatever the
dimmer already gives, which is why `Strobo Rapido` is not a flash of light.
"""

from .. import roles
from ..capability import FixtureCapabilities
from .raises_light import raises_light
from .strobe_written import strobe_capable_offsets, value_strobes


def flash_lights(capability: FixtureCapabilities, written: dict[int, int | None]) -> bool:
    """Whether a scene writing `written` raises light on this fixture."""
    if raises_light(capability, written):
        return True
    if capability.offsets_for_role(roles.DIMMER):
        return False
    for offset, strobing in strobe_capable_offsets(capability).items():
        value = written.get(offset)
        if value is not None and value_strobes(strobing, value):
            return True
    return False
