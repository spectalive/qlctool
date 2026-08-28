"""Which channel offsets fire a smoke machine's pump.

A plain smoke machine types its pump as the master dimmer - it has nothing
else the role could collide with. A fog machine that carries lights has both a
pump and a real LED dimmer, so its pump is typed with the dedicated smoke role
and the dimmer keeps meaning "dimmer". This answers "where is the fog" for
either shape, and it is the only place that question is answered.
"""

from . import roles
from .capability import FixtureCapabilities


def fog_offsets(capability: FixtureCapabilities) -> list[int]:
    """The pump's channel offsets: the smoke role, or the dimmer as fallback."""
    dedicated = capability.offsets_for_role(roles.SMOKE)
    if dedicated:
        return dedicated
    return capability.offsets_for_role(roles.DIMMER)
