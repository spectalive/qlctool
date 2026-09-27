"""Whether a function is putting a colour on a fixture at all."""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from .color_roles import COLOUR
from .show_graph import lit


def fixture_is_coloured(capability: FixtureCapabilities, written: dict[int, int | None]) -> bool:
    """Whether this function is putting a colour on the fixture at all."""
    coloured = {offset for role in COLOUR for offset in capability.offsets_for_role(role)}
    wheel = capability.wheel_for_role(roles.COLOR_MACRO)
    if wheel is not None:
        coloured.add(wheel[0])
    return any(lit(written[o]) for o in coloured if o in written)
