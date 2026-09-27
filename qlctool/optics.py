"""What the `<Physical>` block says about the light itself."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Optics:
    """What the `<Physical>` block says about the light itself.

    Read for the 3D export: a visualiser draws a beam by its angle and its
    output, and points a moving head by how far its pan and tilt travel.
    QLC+ stores degrees and lumens; zero means the definition does not say.
    """

    lumens: float
    degrees_min: float
    degrees_max: float
    pan_max: float
    tilt_max: float
    # `<Layout>`: how the heads are arranged, columns x rows.
    layout: tuple[int, int]
