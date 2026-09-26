"""Whether a scene lights a smoke machine's own LEDs.

A lit smoke machine (`is_lit_smoke`) shows light only when its colour is up:
a dimmer at 255 over red, green and blue at zero is a dark column. So the
column is lit when some colour channel (red, green, blue or white) is written
above zero and, where the machine has a dimmer, that dimmer is lit too. A
definition whose LEDs have no dimmer is judged by its colour alone.
"""

from .. import roles
from ..capability import FixtureCapabilities
from .show_graph import lit


def smoke_column_lit(capability: FixtureCapabilities, written: dict[int, int | None]) -> bool:
    """Whether `written` puts this lit smoke machine's LEDs on."""
    coloured = any(
        lit(written[offset])
        for role in (roles.RED, roles.GREEN, roles.BLUE, roles.WHITE)
        for offset in capability.offsets_for_role(role)
        if offset in written
    )
    dimmers = capability.offsets_for_role(roles.DIMMER)
    if not dimmers:
        return coloured
    return coloured and any(lit(written[o]) for o in dimmers if o in written)
