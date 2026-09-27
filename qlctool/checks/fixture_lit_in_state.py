"""Whether a room state lights a fixture, by dimmer or, lacking one, by colour."""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from .color_roles import COLOUR
from .lit import lit


def fixture_lit_in_state(capability: FixtureCapabilities, written: dict[int, int | None]) -> bool:
    dimmers = capability.offsets_for_role(roles.DIMMER)
    if dimmers:
        return any(lit(written.get(offset, 0)) for offset in dimmers)
    coloured = {offset for role in COLOUR for offset in capability.offsets_for_role(role)}
    return any(lit(written[offset]) for offset in coloured if offset in written)
