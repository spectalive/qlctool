"""Build a Virtual Console <Matrix> - live control of one RGB matrix.

The widget binds to a single RGBMatrix function and offers presets that swap its
algorithm or colour while it runs, which is the one thing a bank of pre-built
matrix functions cannot do. QLC+ 5 renamed the class to VCAnimation but kept the
tag and its children, so one shape serves both.
"""

from collections.abc import Sequence

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state


def build_matrix_control(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
    function_id: int,
    algorithms: Sequence[str] = (),
) -> etree._Element:
    """Algorithms are RGB script names, one preset button each."""
    matrix = etree.SubElement(parent, f"{{{QLC_NS}}}Matrix")
    matrix.set("Caption", caption)
    matrix.set("ID", str(widget_id))

    build_window_state(matrix, x, y, width, height)
    build_appearance(matrix, frame_style="Sunken")

    function = etree.SubElement(matrix, f"{{{QLC_NS}}}Function")
    function.set("ID", str(function_id))
    function.set("InstantApply", "true")

    for index, algorithm in enumerate(algorithms):
        control = etree.SubElement(matrix, f"{{{QLC_NS}}}Control")
        control.set("ID", str(index))
        etree.SubElement(control, f"{{{QLC_NS}}}Type").text = "Animation"
        etree.SubElement(control, f"{{{QLC_NS}}}Resource").text = algorithm

    return matrix
