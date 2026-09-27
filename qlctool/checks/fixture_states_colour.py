"""Whether a fixture's colour channels are lit, in what a function drives."""

from collections.abc import Mapping

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from .color_roles import COLOUR
from .show_graph import lit


def fixture_states_colour(
    capability: FixtureCapabilities | None, written: Mapping[int, int | None]
) -> bool:
    if capability is None or (capability.is_smoke and not capability.is_lit_smoke):
        return False
    offsets = {offset for role in COLOUR for offset in capability.offsets_for_role(role)}
    wheel = capability.wheel_for_role(roles.COLOR_MACRO)
    if wheel is not None:
        offsets.add(wheel[0])
    return any(lit(written[offset]) for offset in offsets if offset in written)
