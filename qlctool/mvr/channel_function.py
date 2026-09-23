"""One GDTF channel function with the attributes the schema insists on."""

from pygdtf import ChannelFunction, DmxValue, NodeLink, PhysicalValue


def channel_function(
    name: str, attribute: str, dmx_from: int, low: float, high: float
) -> ChannelFunction:
    function = ChannelFunction(
        name=name,
        attribute=NodeLink("Attributes", attribute),
        dmx_from=DmxValue(f"{dmx_from}/1"),
        default=DmxValue(f"{dmx_from}/1"),
        physical_from=PhysicalValue(low),
        physical_to=PhysicalValue(high),
    )
    # The schema requires `Default` on every function and forbids it on the
    # channel, so the channel's rest value is the initial function's default.
    function._attr_keys = {"Default", "PhysicalFrom", "PhysicalTo"}
    return function
