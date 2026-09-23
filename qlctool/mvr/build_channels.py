"""The DMX channels of one mode, in GDTF terms.

A mode is an ordered list of channel names; GDTF wants each as a `DMXChannel`
with a 1-based offset, the geometry it drives, and one `ChannelFunction` per
stretch of its range under the right attribute. Three things QLC+ leaves
implicit are made explicit here:

- **A fine channel is not a channel.** `Pan fine` is the low byte of `Pan`, so
  it folds into the coarse channel's offset list (`fine_channel_for`) and
  disappears on its own.
- **Which geometry a channel reaches** is the head it belongs to, or `Yoke` and
  `Head` for pan and tilt, or the beams' parent for anything else - a master
  dimmer above eight pixels, a strobe above four PARs (`channel_geometry`).
- **A range is a function.** Closed, open and strobing are three functions of
  one shutter channel; the slots of a wheel are channel sets of one function,
  the spin after them a second function (`channel_functions`). The visualiser
  reads the attribute of the function the DMX value lands in, which is what
  makes a strobe strobe.
"""

from pygdtf import DmxChannel, LogicalChannel, NodeLink

from ..definition import FixtureDefinition
from .channel_functions import channel_functions
from .channel_geometry import channel_geometry
from .fine_channel_for import FINE_OF, fine_channel_for
from .gdtf_attribute import gdtf_attribute
from .geometry_plan import GeometryPlan
from .wheel_plan import WheelPlan


def build_channels(
    definition: FixtureDefinition,
    mode: str,
    plan: GeometryPlan,
    wheels: WheelPlan,
) -> list[DmxChannel]:
    names = definition.modes[mode]
    channels = [definition.channels[name] for name in names]
    head_of = {
        offset: index for index, head in enumerate(definition.mode_heads(mode)) for offset in head
    }
    fine_used: set[int] = set()
    result = []
    for offset, channel in enumerate(channels):
        if channel.role in FINE_OF:
            continue
        offsets = [offset + 1]
        fine = fine_channel_for(channel, channels, offset, fine_used)
        if fine is not None:
            fine_used.add(fine)
            offsets.append(fine + 1)
        geometry = channel_geometry(channel, head_of.get(offset), plan)
        attribute = gdtf_attribute(channel)
        functions = channel_functions(channel, attribute, definition, wheels)
        first = functions[0]
        result.append(
            DmxChannel(
                dmx_break=1,
                offset=offsets,
                default=None,
                geometry=geometry,
                logical_channels=[
                    LogicalChannel(
                        attribute=NodeLink("Attributes", attribute), channel_functions=functions
                    )
                ],
                initial_function=NodeLink(
                    "DMXChannel", f"{geometry}_{attribute}.{first.attribute}.{first.name}"
                ),
            )
        )
    return result
