"""Build a QLC+ EFX <Function> element - the moving-head pattern generator.

An EFX sweeps pan/tilt through a geometric path. Each participating fixture gets
its own head, mode, direction and phase offset, then the shared block describes
the shape (algorithm, width/height/rotation) and the two axes. Child order here
is the order the production workspaces use.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from lxml import etree

from ..constants import QLC_NS


@dataclass(frozen=True)
class EFXFixture:
    """One fixture's participation in an EFX.

    start_offset is the phase in degrees (0-359) that spreads fixtures around
    the path. mode is the EFX fixture mode QLC+ stores; the show only uses 0.
    """

    fixture_id: int
    head: int = 0
    mode: int = 0
    direction: str = "Forward"
    start_offset: int = 0


@dataclass(frozen=True)
class EFXAxis:
    """One axis of the path: its centre, how fast it cycles, its phase."""

    offset: int = 127
    frequency: int = 2
    phase: int = 0


def build_efx(
    function_id: int,
    name: str,
    fixtures: Sequence[EFXFixture],
    algorithm: str = "Circle",
    x_axis: EFXAxis | None = None,
    y_axis: EFXAxis | None = None,
    width: int = 100,
    height: int = 100,
    rotation: int = 0,
    start_offset: int = 0,
    is_relative: int = 0,
    propagation_mode: str = "Parallel",
    direction: str = "Forward",
    run_order: str = "Loop",
    fade_in: int = 0,
    fade_out: int = 0,
    duration: int = 6848,
    path: str | None = None,
) -> etree._Element:
    """Return a `<Function Type="EFX">` element.

    algorithm is one of efx_algorithms.EFX_ALGORITHMS. propagation_mode is
    Parallel / Serial / Asymmetric. The axis defaults (X phase 90, Y phase 0)
    are what QLC+ writes for a plain circle.
    """
    function = etree.Element(f"{{{QLC_NS}}}Function")
    function.set("ID", str(function_id))
    function.set("Type", "EFX")
    function.set("Name", name)
    if path is not None:
        function.set("Path", path)

    for fixture in fixtures:
        element = etree.SubElement(function, f"{{{QLC_NS}}}Fixture")
        _child(element, "ID", fixture.fixture_id)
        _child(element, "Head", fixture.head)
        _child(element, "Mode", fixture.mode)
        _child(element, "Direction", fixture.direction)
        _child(element, "StartOffset", fixture.start_offset)

    _child(function, "PropagationMode", propagation_mode)

    speed = etree.SubElement(function, f"{{{QLC_NS}}}Speed")
    speed.set("FadeIn", str(fade_in))
    speed.set("FadeOut", str(fade_out))
    speed.set("Duration", str(duration))

    _child(function, "Direction", direction)
    _child(function, "RunOrder", run_order)
    _child(function, "Algorithm", algorithm)
    _child(function, "Width", width)
    _child(function, "Height", height)
    _child(function, "Rotation", rotation)
    _child(function, "StartOffset", start_offset)
    _child(function, "IsRelative", is_relative)

    _axis(function, "X", x_axis if x_axis is not None else EFXAxis(phase=90))
    _axis(function, "Y", y_axis if y_axis is not None else EFXAxis(frequency=3))

    return function


def _child(parent: etree._Element, name: str, value: object) -> etree._Element:
    element = etree.SubElement(parent, f"{{{QLC_NS}}}{name}")
    element.text = str(value)
    return element


def _axis(parent: etree._Element, name: str, axis: EFXAxis) -> None:
    element = etree.SubElement(parent, f"{{{QLC_NS}}}Axis")
    element.set("Name", name)
    _child(element, "Offset", axis.offset)
    _child(element, "Frequency", axis.frequency)
    _child(element, "Phase", axis.phase)
