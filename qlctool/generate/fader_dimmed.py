"""Whether a fixture has a dimmer the intensity chases may sweep.

A blade dimmer is not a fader: an EFX sweeping it does not dip the beam, it
slides a blade across the lens (`stepped_dimmer`). A smoke machine's level is
its pump. Neither is a dimmer a chase may run.
"""

from .. import roles
from ..capability import FixtureCapabilities
from ..stepped_dimmer import stepped_dimmer_offsets


def fader_dimmed(capability: FixtureCapabilities) -> bool:
    """True when the fixture is not smoke and its dimmer is a plain fader."""
    return (
        not capability.is_smoke
        and bool(capability.offsets_for_role(roles.DIMMER))
        and not stepped_dimmer_offsets(capability)
    )
