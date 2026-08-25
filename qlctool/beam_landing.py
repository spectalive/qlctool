"""Where a fixture's beam actually meets the floor.

Aiming a rig by looking at the 3D preview and nudging an angle is how this plot
ended up lighting the DJ in the face: the truss PARs sat at 35 degrees off
vertical, which from four metres up lands them at z=4485 - the DJ deck is at
4500. It looked like "tilted towards the audience" and it was, by two metres too
few. So the plot is checked with arithmetic instead.

`x_rot` turns a fixture about the horizontal axis **by minus the stored angle**:
`MonitorProperties::fixtureRotationMatrix` builds it as
`QQuaternion::fromAxisAndAngle(QVector3D(1, 0, 0), -rot.x())`, matching what
`Qt3DCore::QTransform::fromAxesAndAngles` does in the 3D view.

**Which way the light leaves depends on how QLC+ draws the fixture**, and there
are two answers. A fixture with a mesh - a PAR, a moving head - emits along
`(0, -1, 0)`, straight down, which is how a light hangs. A fixture QLC+ draws
itself instead of loading a mesh - `LED Bar (Pixels)`, `LED Bar (Beams)`,
`Strobe` - has its emitting faces on its **top**: `PixelBar3DItem.qml` puts each
head's `PlaneMesh` at `+(phySize.y / 2)`, and a Qt3D plane faces `+Y`. So the
same angle points those two kinds of fixture in opposite directions.

Rotating `(0, e, 0)` - where `e` is -1 for a mesh and +1 for a drawn bar - by
minus the angle gives `(0, e*cos, -e*sin)`. Depth grows towards the audience, so
for a PAR a **positive** angle leans out over them, and for a pixel bar a
**negative** one does.

Both halves of that were learnt the hard way on 2026-08-25, in the 3D view and
not here: first the whole file had the sign backwards and the back truss lit the
rear wall, then flipping it uniformly turned the pixel panels and the LED bars
around, which had been right all along. A sign convention is read out of the
renderer's source, and it is read per fixture type.

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

# Fixture types QLC+ draws itself rather than loading a mesh for. Their light
# leaves the top face, not the bottom - see the module docstring.
UPWARD_TYPES = frozenset({
    "led bar (pixels)", "led bar (beams)", "strobe",
})


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
