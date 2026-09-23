"""One channel function per run of capabilities that share a GDTF attribute.

Consecutive QLC+ ranges that map to the same attribute (`gdtf_range_attribute`)
become one function whose channel sets are those ranges; the wheel functions
point at the wheel `build_wheels` made and index its slots.
"""

from pygdtf import ChannelFunction, ChannelSet, DmxValue, NodeLink, PhysicalValue

from ..definition import Capability, Channel
from .channel_function import channel_function
from .gdtf_name import gdtf_name
from .gdtf_range_attribute import gdtf_range_attribute
from .ranged_physical import ranged_physical
from .set_physical import set_physical
from .wheel_plan import WheelPlan

WHEEL_FUNCTIONS = frozenset({"Color1", "Gobo1", "Gobo1SelectShake"})


def ranged_functions(channel: Channel, attribute: str, wheels: WheelPlan) -> list[ChannelFunction]:
    groups: list[tuple[str, list[tuple[int, Capability]]]] = []
    for index, capability in enumerate(channel.capabilities):
        target = gdtf_range_attribute(attribute, capability)
        if groups and groups[-1][0] == target:
            groups[-1][1].append((index, capability))
        else:
            groups.append((target, [(index, capability)]))

    functions = []
    counts: dict[str, int] = {}
    wheel = wheels.by_channel.get(channel.name)
    for target, members in groups:
        counts[target] = counts.get(target, 0) + 1
        first = members[0][1]
        low, high = ranged_physical(target, first)
        function = channel_function(f"{target} {counts[target]}", target, first.minimum, low, high)
        if wheel and target in WHEEL_FUNCTIONS:
            function.wheel = NodeLink("WheelCollect", wheel)
        for index, capability in members:
            slot = wheels.slot_index.get((channel.name, index), 0)
            physical = set_physical(target, capability)
            function.channel_sets.append(
                ChannelSet(
                    name=gdtf_name(capability.name),
                    dmx_from=DmxValue(f"{capability.minimum}/1"),
                    physical_from=PhysicalValue(physical),
                    physical_to=PhysicalValue(physical),
                    wheel_slot_index=slot,
                )
            )
        functions.append(function)
    return functions
