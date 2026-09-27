"""Whether a scene says a colour on a fixture that has red, green, blue."""

from .. import roles
from .color_roles import COLOUR
from .driven_channels import Driven
from .show_graph import ShowGraph, lit


def states_rgb_colour(graph: ShowGraph, stated: Driven) -> bool:
    for fixture_id, written in stated.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke or not written:
            continue
        if not any(capability.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE)):
            continue
        offsets = {o for role in COLOUR for o in capability.offsets_for_role(role)}
        if any(lit(written[o]) for o in offsets if o in written):
            return True
    return False
