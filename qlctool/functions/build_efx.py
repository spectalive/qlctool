"""Build a QLC+ EFX <Function> element - the moving-head pattern generator.

An EFX sweeps pan/tilt through a geometric path. Each participating fixture gets
its own head, mode, direction and phase offset, then the shared block describes
the shape (algorithm, width/height/rotation) and the two axes. Child order here
is the order the production workspaces use.
"""

from collections.abc import Sequence

from lxml import etree

from ..constants import QLC_NS
from .axis import axis
from .child import child
from .efx import EFXFixture
from .efx_axis import EFXAxis


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
        child(element, "ID", fixture.fixture_id)
        child(element, "Head", fixture.head)
        child(element, "Mode", fixture.mode)
        child(element, "Direction", fixture.direction)
        child(element, "StartOffset", fixture.start_offset)

    child(function, "PropagationMode", propagation_mode)

    speed = etree.SubElement(function, f"{{{QLC_NS}}}Speed")
    speed.set("FadeIn", str(fade_in))
    speed.set("FadeOut", str(fade_out))
    speed.set("Duration", str(duration))

    child(function, "Direction", direction)
    child(function, "RunOrder", run_order)
    child(function, "Algorithm", algorithm)
    child(function, "Width", width)
    child(function, "Height", height)
    child(function, "Rotation", rotation)
    child(function, "StartOffset", start_offset)
    child(function, "IsRelative", is_relative)

    axis(function, "X", x_axis if x_axis is not None else EFXAxis(phase=90))
    axis(function, "Y", y_axis if y_axis is not None else EFXAxis(frequency=3))

    return function
