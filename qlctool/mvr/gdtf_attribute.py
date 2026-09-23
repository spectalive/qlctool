"""The GDTF attribute a QLC+ channel stands for.

GDTF names what a channel does with a fixed vocabulary (Annex B of DIN SPEC
15800), and a visualiser renders only the names it knows: BlenderDMX reads
Dimmer, Pan, Tilt, the ColorAdd mix, the Color1 and Gobo1 wheels, Shutter1 and
Shutter1Strobe, Zoom, Focus1. A channel mapped to the wrong name is a channel
the picture ignores, so this reasons from the role the toolkit already derives
(preset first, group and name as fallback), never from the channel's label.

A channel nothing renders still needs a legal name: `NoFeature` is what GDTF
reserves for exactly that. The fog pump lands there too - GDTF 1.2 has no
attribute for it that the Annex data knows.
"""

from .. import roles
from ..definition import Channel

NO_FEATURE = "NoFeature"

_BY_ROLE = {
    roles.RED: "ColorAdd_R",
    roles.GREEN: "ColorAdd_G",
    roles.BLUE: "ColorAdd_B",
    roles.WHITE: "ColorAdd_W",
    roles.AMBER: "ColorAdd_RY",
    roles.UV: "ColorAdd_UV",
    roles.CYAN: "ColorSub_C",
    roles.MAGENTA: "ColorSub_M",
    roles.YELLOW: "ColorSub_Y",
    roles.DIMMER: "Dimmer",
    roles.PAN: "Pan",
    roles.TILT: "Tilt",
    roles.STROBE: "Shutter1",
    roles.COLOR_MACRO: "Color1",
    roles.GOBO: "Gobo1",
    roles.PRISM: "Prism1",
    roles.PRISM_ROTATION: "Prism1PosRotate",
    roles.GOBO_SHAKE: "Gobo1WheelShake",
    roles.EFFECT: "Effects1",
    roles.FOCUS: "Focus1",
    roles.ZOOM: "Zoom",
    roles.SPEED: "PositionMSpeed",
    roles.SMOKE: NO_FEATURE,
}


def gdtf_attribute(channel: Channel) -> str:
    """The Annex B attribute for this channel, `NoFeature` when none applies."""
    if channel.role in _BY_ROLE:
        return _BY_ROLE[channel.role]
    if channel.group == "Maintenance" and "reset" in channel.name.lower():
        return "FixtureGlobalReset"
    return NO_FEATURE
