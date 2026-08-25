"""Where a fixture's beam actually meets the floor.

Aiming a rig by looking at the 3D preview and nudging an angle is how this plot
ended up lighting the DJ in the face: the truss PARs sat at 35 degrees off
vertical, which from four metres up lands them at z=4485 - the DJ deck is at
4500. It looked like "tilted towards the audience" and it was, by two metres too
few. So the plot is checked with arithmetic instead.

QLC+ sends light along `(0, -1, 0)` and `x_rot` turns it about the horizontal
axis, giving `(0, -cos, -sin)`. Depth grows towards the audience, so a negative
angle leans out over them and a positive one leans back over the stage.

**A moving head cannot be aimed this way and must not be.** Its rotation is how
the body is *mounted* - hanging (0) or standing on the floor (180) - and where
the beam goes is pan and tilt, which the show drives. Tilting the mounting of a
mover just leaves it sitting crooked on its clamp.
"""

import math
from dataclasses import dataclass

from . import roles
from .capability import FixtureCapabilities
from .monitor_node import MonitorItem

# The only two ways a moving head is ever rigged.
HANGING = 0
STANDING = 180


@dataclass(frozen=True)
class Landing:
    fixture_id: int
    # Depth at which the beam meets the floor, in mm. None when it never does.
    z: float | None
    reason: str


def beam_landing(item: MonitorItem, capabilities: FixtureCapabilities) -> Landing:
    """Where this fixture's beam lands, or why the question does not apply."""
    if capabilities.has_role(roles.PAN) and capabilities.has_role(roles.TILT):
        return Landing(item.fixture_id, None, "moving head: pan and tilt aim it")
    if capabilities.is_smoke:
        return Landing(item.fixture_id, None, "smoke machine: no beam")

    angle = math.radians(item.x_rot)
    down, out = -math.cos(angle), -math.sin(angle)
    # cos(90 degrees) is 6e-17 rather than 0 in floating point, and dividing by
    # it sends the landing to the far side of the solar system.
    if down > -1e-6:
        return Landing(item.fixture_id, None, "aimed level or upward")

    depth = capabilities.dimensions.depth if capabilities.dimensions else 0.0
    centre = item.z + depth / 2
    travel = item.y / -down
    return Landing(item.fixture_id, centre + out * travel, "")
