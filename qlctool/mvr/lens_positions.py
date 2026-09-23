"""Where each lens sits under its parent, in metres: a grid across the top.

The grid is the definition's `<Layout>` when it matches the head count, else
one row; a mover's lenses sit on top of its head, a static fixture's on top
of its body.
"""

from ..definition import FixtureDefinition

LENS_THICKNESS = 0.02


def lens_positions(
    definition: FixtureDefinition,
    beams: int,
    width: float,
    depth: float,
    height: float,
    moving: bool,
) -> list[tuple[float, float, float]]:
    if beams == 0:
        return []
    columns, rows = definition.optics.layout if definition.optics else (1, 1)
    if columns * rows != beams:
        columns, rows = beams, 1
    top = (0.35 * height) / 2 if moving else height + LENS_THICKNESS / 2
    positions = []
    for index in range(beams):
        column, row = index % columns, index // columns
        x = -width / 2 + width * (column + 0.5) / columns
        y = depth / 2 - depth * (row + 0.5) / rows
        positions.append((x, y, top))
    return positions
