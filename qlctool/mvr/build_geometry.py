"""The geometry tree a definition gets: a body, and a beam per head.

GDTF draws a fixture from named geometries, and a visualiser lights a beam
only where a `Beam` geometry sits. QLC+ says nothing about shape beyond
`<Dimensions>` and, for a bar, how many `<Head>`s a mode declares - so the
model is built from those: a box (or the base, yoke and head primitives for a
mover) sized from the definition, with one small lens per head laid out across
the width. Every fixture is modelled standing on its base with the lenses
pointing up; how it hangs in the room is the MVR matrix's business.

The names matter because DMX channels point at them: a colour channel inside
head 3 drives `Beam3`, pan turns `Yoke`, tilt turns `Head`, and a channel no
head claims - a master dimmer, the strobe of a bar - lands on the parent of the
beams, where GDTF lets it reach all of them.
"""

from pygdtf import Geometry, GeometryAxis

from .. import roles
from ..definition import FixtureDefinition
from .beam_geometry import beam_geometry
from .gdtf_matrix import gdtf_matrix
from .geometry_model import geometry_model
from .geometry_plan import GeometryPlan
from .has_role import has_role
from .lens_positions import LENS_THICKNESS, lens_positions

# Millimetres in QLC+; GDTF models are in metres.
MM = 1000.0
# What a definition that says nothing gets, in metres.
FALLBACK_SIZE = 0.3
COLOUR_ROLES = frozenset(
    {
        roles.RED,
        roles.GREEN,
        roles.BLUE,
        roles.WHITE,
        roles.AMBER,
        roles.UV,
        roles.CYAN,
        roles.MAGENTA,
        roles.YELLOW,
        roles.COLOR_MACRO,
        roles.GOBO,
    }
)


def build_geometry(definition: FixtureDefinition) -> GeometryPlan:
    size = definition.dimensions
    width = (size.width / MM) if size and size.width else FALLBACK_SIZE
    height = (size.height / MM) if size and size.height else FALLBACK_SIZE
    depth = (size.depth / MM) if size and size.depth else FALLBACK_SIZE

    head_counts = [len(heads) for heads in definition.heads.values()]
    heads = max(head_counts) if head_counts else 0
    # A smoke machine's "dimmer" is its pump: a box on the floor, no lens.
    coloured = any(channel.role in COLOUR_ROLES for channel in definition.channels.values())
    dimmed = any(channel.role == roles.DIMMER for channel in definition.channels.values())
    lit = coloured or (dimmed and definition.fixture_type.lower() != "smoke")
    beams = max(heads, 1) if lit else 0
    moving = has_role(definition, roles.PAN) and has_role(definition, roles.TILT)
    spot = has_role(definition, roles.GOBO)

    lens = max(0.05, 0.8 * min(width / max(beams, 1), depth))
    if moving:
        lens = max(0.05, 0.6 * min(width, depth))
    lens_model = geometry_model("Lens", lens, lens, LENS_THICKNESS, "Cylinder")
    beam_geometries = [
        beam_geometry(index, x, y, z, lens, spot, definition)
        for index, (x, y, z) in enumerate(
            lens_positions(definition, beams, width, depth, height, moving), start=1
        )
    ]
    beam_names = tuple(beam.name for beam in beam_geometries)

    if moving:
        base_h, yoke_h, head_h = 0.25 * height, 0.45 * height, 0.35 * height
        models = [
            geometry_model("Base", width, depth, base_h, "Base"),
            geometry_model("Yoke", 0.9 * width, 0.9 * depth, yoke_h, "Yoke"),
            geometry_model("Head", 0.6 * width, 0.6 * depth, head_h, "Head"),
            lens_model,
        ]
        head = GeometryAxis(
            name="Head",
            model="Head",
            position=gdtf_matrix(0, 0, 0.7 * yoke_h),
            geometries=beam_geometries,
        )
        yoke = GeometryAxis(
            name="Yoke", model="Yoke", position=gdtf_matrix(0, 0, base_h), geometries=[head]
        )
        root = Geometry(name="Base", model="Base", position=gdtf_matrix(0, 0, 0), geometries=[yoke])
        return GeometryPlan(
            models=models,
            root=root,
            root_name="Base",
            beams=beam_names,
            emitter="Head" if len(beam_names) != 1 else beam_names[0],
            pan="Yoke",
            tilt="Head",
        )

    models = [geometry_model("Body", width, depth, height, "Cube"), lens_model]
    root = Geometry(
        name="Body", model="Body", position=gdtf_matrix(0, 0, 0), geometries=beam_geometries
    )
    return GeometryPlan(
        models=models,
        root=root,
        root_name="Body",
        beams=beam_names,
        emitter="Body" if len(beam_names) != 1 else beam_names[0],
        pan=None,
        tilt=None,
    )
