"""One `Beam` geometry: the lens a visualiser lights, flipped to point up.

Angle and flux come from the definition's `<Lens>` and `<Bulb>` where stated;
a spot (gobo wheel) that says nothing gets a tight beam, a wash a wide one.
"""

from pygdtf import BeamType, GeometryBeam, LampType

from ..definition import FixtureDefinition
from .gdtf_matrix import gdtf_matrix


def beam_geometry(
    index: int,
    x: float,
    y: float,
    z: float,
    lens: float,
    spot: bool,
    definition: FixtureDefinition,
) -> GeometryBeam:
    optics = definition.optics
    angle = optics.degrees_max if optics and optics.degrees_max else 0.0
    if not angle:
        angle = optics.degrees_min if optics and optics.degrees_min else (5.0 if spot else 25.0)
    lumens = optics.lumens if optics and optics.lumens else 2000.0
    return GeometryBeam(
        name=f"Beam{index}",
        model="Lens",
        position=gdtf_matrix(x, y, z, flipped=True),
        lamp_type=LampType("LED"),
        power_consumption=100,
        luminous_flux=lumens,
        color_temperature=6500,
        beam_angle=angle,
        field_angle=angle,
        beam_radius=lens / 2,
        beam_type=BeamType("Spot" if spot else "Wash"),
        color_rendering_index=90,
    )
