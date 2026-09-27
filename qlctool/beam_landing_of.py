"""Where a patched fixture's beam actually meets the floor, or why it does not."""

import math

from . import roles
from .beam_landing import UPWARD_TYPES, Landing
from .fixture_capabilities import FixtureCapabilities
from .monitor_node import MonitorItem


def beam_landing(item: MonitorItem, capabilities: FixtureCapabilities) -> Landing:
    """Where this fixture's beam lands, or why the question does not apply."""
    if capabilities.has_role(roles.PAN) and capabilities.has_role(roles.TILT):
        return Landing(item.fixture_id, None, "moving head: pan and tilt aim it")
    if capabilities.is_smoke:
        return Landing(item.fixture_id, None, "smoke machine: no beam")

    angle = math.radians(item.x_rot)
    emission = 1.0 if capabilities.fixture_type.lower() in UPWARD_TYPES else -1.0
    down, out = emission * math.cos(angle), -emission * math.sin(angle)
    # cos(90 degrees) is 6e-17 rather than 0 in floating point, and dividing by
    # it sends the landing to the far side of the solar system.
    if down > -1e-6:
        return Landing(item.fixture_id, None, "aimed level or upward")

    depth = capabilities.dimensions.depth if capabilities.dimensions else 0.0
    centre = item.z + depth / 2
    travel = item.y / -down
    return Landing(item.fixture_id, centre + out * travel, "")
