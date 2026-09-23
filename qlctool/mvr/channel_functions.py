"""The channel functions one DMX channel gets under its attribute.

A channel whose ranges change meaning - shutter, colour wheel, gobo wheel,
prism - gets one function per stretch (`ranged_functions`). A preset-only
strobe channel gets an open value at zero and a strobe above it, because
QLC+ only says "slow to fast" over the whole range and on every LED PAR
here zero is simply open. Anything else is one function over the whole
range, with pan and tilt resting at the middle.
"""

from pygdtf import ChannelFunction, DmxValue

from ..definition import Channel, FixtureDefinition
from .channel_function import channel_function
from .physical_range import DEFAULT_STROBE_HZ, physical_range
from .ranged_functions import ranged_functions
from .wheel_plan import WheelPlan

RANGED = frozenset({"Shutter1", "Color1", "Gobo1", "Prism1"})
CENTRED = frozenset({"Pan", "Tilt"})


def channel_functions(
    channel: Channel,
    attribute: str,
    definition: FixtureDefinition,
    wheels: WheelPlan,
) -> list[ChannelFunction]:
    if attribute in RANGED and channel.capabilities:
        return ranged_functions(channel, attribute, wheels)
    if attribute == "Shutter1":
        return [
            channel_function("Open", "Shutter1", 0, 1.0, 1.0),
            channel_function("Strobe", "Shutter1Strobe", 1, *DEFAULT_STROBE_HZ),
        ]
    low, high = physical_range(attribute, definition)
    function = channel_function(attribute, attribute, 0, low, high)
    if attribute in CENTRED:
        function.default = DmxValue("128/1")
    return [function]
