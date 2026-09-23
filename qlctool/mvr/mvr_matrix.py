"""Where a QLC+ fixture stands in MVR terms: one matrix from the plot's numbers.

Two coordinate systems, one rig. QLC+ draws with y up and z growing towards the
audience, and stores a fixture by its near corner in millimetres. MVR (and
GDTF, and Blender) put z up and y upstage, place a fixture by the origin of its
model - the middle of the base - and centre the room on nothing in particular,
so the stage is centred here: x across from house left, y from the front edge
back, z from the floor.

Every GDTF this export writes is modelled standing, lens up. QLC+ meshes hang -
a PAR at `x_rot=0` points at the floor - so a meshed fixture is turned a half
turn about X first and then by QLC+'s own rotation, which is **minus** the
stored angle (`MonitorProperties::fixtureRotationMatrix`); a fixture QLC+
draws itself lights from its top face and needs only the second turn. The
rule per type is the one `beam_landing` derived from the renderer's source,
and a smoke machine is a box on the floor whatever its mesh emits. Positive
`x_rot` on a truss PAR still leans it out over the audience; check with the
tests before trusting the picture.

BlenderDMX reads the four groups of an MVR matrix as the images of the three
axes and the translation (`get_matrix` in its `mvr.py` transposes them), in
millimetres.
"""

from pymvr import Matrix

from ..beam_landing import UPWARD_TYPES
from ..definition import FixtureDefinition
from ..monitor_node import MonitorItem
from .apply_rotation import apply_rotation
from .clean_value import clean_value
from .multiply_rotations import multiply_rotations
from .rotation_about_x import rotation_about_x
from .rotation_about_z import rotation_about_z

SMOKE_TYPE = "smoke"


def mvr_matrix(
    item: MonitorItem,
    definition: FixtureDefinition,
    stage: tuple[float, float, float],
) -> Matrix:
    size = definition.dimensions
    width = size.width if size else 0.0
    height = size.height if size else 0.0
    depth = size.depth if size else 0.0

    kind = definition.fixture_type.lower()
    upward = kind == SMOKE_TYPE or kind in UPWARD_TYPES
    about_x = -item.x_rot if upward else 180.0 - item.x_rot
    rotation = multiply_rotations(rotation_about_z(-item.y_rot), rotation_about_x(about_x))

    # The centre of the box QLC+ draws, in MVR axes.
    centre = (
        item.x + width / 2 - stage[0] / 2,
        stage[2] / 2 - (item.z + depth / 2),
        item.y + height / 2,
    )
    # The model's origin is the middle of its base; put its centre on QLC+'s.
    half_up = apply_rotation(rotation, (0.0, 0.0, height / 2))
    translation = tuple(c - h for c, h in zip(centre, half_up, strict=True))

    columns = [[clean_value(rotation[row][col]) for row in range(3)] + [0.0] for col in range(3)]
    return Matrix(columns + [[clean_value(t) for t in translation] + [0.0]])
