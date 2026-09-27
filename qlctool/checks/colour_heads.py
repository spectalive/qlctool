"""How many of a fixture's declared heads carry a full RGB set of their own."""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities

COLOUR_ROLES = (roles.RED, roles.GREEN, roles.BLUE)


def colour_heads(capability: FixtureCapabilities) -> int:
    """How many declared heads carry a full RGB set of their own."""
    by_role = {role: set(capability.offsets_for_role(role)) for role in COLOUR_ROLES}
    return sum(
        1
        for head in capability.declared_heads
        if all(by_role[role] & set(head) for role in COLOUR_ROLES)
    )
