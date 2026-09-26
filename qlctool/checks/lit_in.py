"""Whether a fixture is lit by what is driving it at one instant.

Its dimmer decides when it has one - on the BEAM 7R that is the blade. A
fixture with no dimmer is lit by any HTP channel written above zero: its
colour is its light. `htp` is that fixture's HTP offsets (`merged_htp`).
"""

from collections.abc import Collection, Mapping

from .. import roles
from ..capability import FixtureCapabilities
from .show_graph import lit


def lit_in(
    capability: FixtureCapabilities, written: Mapping[int, int | None], htp: Collection[int]
) -> bool:
    """True when `written` opens this fixture's light."""
    dimmers = capability.offsets_for_role(roles.DIMMER)
    if dimmers:
        return any(offset in written and lit(written[offset]) for offset in dimmers)
    return any(offset in written and lit(written[offset]) for offset in htp)
