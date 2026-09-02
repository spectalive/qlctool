"""Park the beams' continuous half-colour channel, on every look that picks a colour.

The BEAM 230W 7R carries its colour on two channels: the wheel (channel 8,
labelled positions) and a second Colour channel with one unlabelled 0-255
range - the "half-colour position", which slides the wheel between two detents
so one beam shows two colours at once. The `MultiColor BEAM` buttons use it,
and they are Toggles: press one, release it, and QLC+ takes the button's fader
away without writing anything back. The channel is LTP, so it keeps 255 - and
no room state, no bank and no work light had ever written it, so from that
press on every colour the wheel picked came out split in two for the rest of
the night (cross-audit, 2026-09-02).

So every scene that states a wheel colour states this channel too, at zero,
the way it already parks the mode channel: a colour is a whole wheel position,
not half of one. Found by shape - the Colour-role channel beside the wheel
whose only range spans the whole channel - never by model.
"""

from . import roles
from .capability import FixtureCapabilities


def multicolor_off_pairs(capabilities: FixtureCapabilities) -> list[tuple[int, int]]:
    """(offset, 0) for every continuous colour-shift channel beside the wheel."""
    wheel = capabilities.wheel_for_role(roles.COLOR_MACRO)
    if wheel is None:
        return []
    wheel_offset, _ = wheel
    pairs: list[tuple[int, int]] = []
    for offset in capabilities.offsets_for_role(roles.COLOR_MACRO):
        if offset == wheel_offset:
            continue
        ranges = capabilities.capabilities_by_offset[offset]
        if len(ranges) == 1 and ranges[0].minimum == 0 and ranges[0].maximum == 255:
            pairs.append((offset, 0))
    return pairs
