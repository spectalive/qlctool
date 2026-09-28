"""A piece of scenery in the 3D view - QLC+ calls it a MeshItem.

Shared by the two things that can decide a rig's positions - the generated
band layout and a written stage plot - because the node itself is the same
either way. Child order follows `MonitorProperties::saveXML`: Font,
ChannelStyle, ValueStyle, Grid, StageItem, then one FxItem per fixture.

Two details QLC+ does not forgive:

- **The grid is in metres and the positions in millimetres**, and a position is
  the fixture's near corner, not its centre - QLC+ adds half the mesh extents
  when it draws, so `y=0` is standing on the floor.
- **The point of view is written even though it is optional.** With none
  stored, the 2D view asks for one on first open and then converts every
  position it has into it, silently rewriting a layout that was already right.
"""

from dataclasses import dataclass

# MonitorProperties::PointOfView in the QLC+ source, by name.
POINTS_OF_VIEW = {"top": 1, "front": 2, "right": 3, "left": 4}


@dataclass(frozen=True)
class PropItem:
    """A piece of scenery in the 3D view - QLC+ calls it a MeshItem.

    Given in world terms: the centre of the box, in millimetres above the floor,
    and how big it is. QLC+ stores something less friendly - it positions a
    generic mesh by a corner *and* adds half the raw mesh's extents, which for
    its own primitives is a fixed metre whatever the scale, so the stored
    position is the wanted centre minus 1000 on every axis. That conversion
    lives in `write_monitor` rather than in whoever writes a plot.
    """

    item_id: int
    resource: str
    name: str
    centre: tuple[float, float, float]
    size: tuple[float, float, float]
    x_rot: float = 0.0
    y_rot: float = 0.0
    z_rot: float = 0.0


# QLC+'s bundled primitives all span -1..1, so two metres across before scaling.
PRIMITIVE_SIZE = 2000.0
