"""Whether a fixture is lit by what is driving it at one instant.

Its dimmer decides when it has one - on the BEAM 7R that is the blade. A
fixture with no dimmer is lit by any Intensity channel written above zero: its
colour is its light.
"""

from collections.abc import Mapping

from .. import roles
from ..capability import FixtureCapabilities
from .show_graph import lit

INTENSITY_GROUP = "Intensity"


def lit_in(capability: FixtureCapabilities, written: Mapping[int, int | None]) -> bool:
    """True when `written` opens this fixture's light."""
    dimmers = capability.offsets_for_role(roles.DIMMER)
    if dimmers:
        return any(offset in written and lit(written[offset]) for offset in dimmers)
    return any(
        group == INTENSITY_GROUP and offset in written and lit(written[offset])
        for offset, group in enumerate(capability.groups_by_offset)
    )
