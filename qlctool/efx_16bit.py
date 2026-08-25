"""Whether a fixture lets an EFX keep its 16-bit handling on.

`EFXFixture` caches its channels when an EFX starts and, if a fine channel is
not directly after its coarse one, calls `fader->setHandleSecondary(false)`.
That fader belongs to the **EFX**, not to the fixture - so one badly ordered
fixture turns 16 bit off for every fixture in the same EFX.

That is what stopped the CromoWash100 moving. Its channels are
`Pan, Pan fine, Tilt, Tilt fine`, properly paired; the BEAM 230W 7R in the same
EFX is `Pan, Tilt, Pan fine, Tilt fine`, two apart, and it flipped the flag for
everybody. The washes then had their coarse channels written as part of a 16-bit
value that nothing split, so pan and tilt sat at 0 and only the fine channels
moved - one 256th of the range.

QLC+ makes the same check per EFX mode, on whichever channels that mode drives:
pan and tilt for a movement EFX, the intensity channel for a dimmer one. Pass
the pairs for the mode being generated. A fixture with no fine channel at all is
on the 16-bit side of the fence: it never trips the check, so it can share an
EFX with the ones that pair.
"""

from . import roles
from .capability import FixtureCapabilities

# EFXFixture::PanTilt drives these...
PAN_TILT_PAIRS = ((roles.PAN, roles.PAN_FINE), (roles.TILT, roles.TILT_FINE))
# ...and EFXFixture::Dimmer this one.
INTENSITY_PAIRS = ((roles.DIMMER, roles.DIMMER_FINE),)


def keeps_16bit(
    capabilities: FixtureCapabilities,
    pairs: tuple[tuple[str, str], ...] = PAN_TILT_PAIRS,
) -> bool:
    """False when this fixture would turn 16-bit off for its whole EFX."""
    for coarse_role, fine_role in pairs:
        coarse = capabilities.offsets_for_role(coarse_role)
        fine = capabilities.offsets_for_role(fine_role)
        if not fine:
            continue
        if not coarse or fine[0] - coarse[0] != 1:
            return False
    return True
