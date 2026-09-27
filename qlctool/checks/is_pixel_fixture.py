"""Whether a fixture is a pixel panel: colour, no movement, a named internal programme."""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from ..internal_program import internal_program
from .families import FAMILIES


def is_pixel_fixture(capability: FixtureCapabilities) -> bool:
    """True for a colour fixture that does not move and runs a programme of its own."""
    return (
        not capability.is_smoke
        and bool(capability.roles & FAMILIES["color"])
        and not bool(capability.roles & FAMILIES["position"])
        and roles.EFFECT in capability.roles
        and internal_program(capability) is not None
    )
