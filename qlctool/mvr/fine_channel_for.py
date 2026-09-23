"""The fine channel a coarse one owns, if the mode has one it has not used yet.

QLC+ lists `Pan` and `Pan fine` as two channels; GDTF wants one channel with
two offsets. The first unclaimed fine channel after the coarse one is its low
byte - the order every definition in this rig uses.
"""

from .. import roles
from ..definition import Channel

FINE_OF = {
    roles.PAN_FINE: roles.PAN,
    roles.TILT_FINE: roles.TILT,
    roles.DIMMER_FINE: roles.DIMMER,
}


def fine_channel_for(
    channel: Channel, channels: list[Channel], offset: int, used: set[int]
) -> int | None:
    wanted = next((fine for fine, coarse in FINE_OF.items() if coarse == channel.role), None)
    if wanted is None:
        return None
    for index in range(offset + 1, len(channels)):
        if channels[index].role == wanted and index not in used:
            return index
    return None
