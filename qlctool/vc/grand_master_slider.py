"""Build the Virtual Console <Slider> that drives the workspace's GrandMaster.

The workspace's <Properties> already carries a <GrandMaster> value - the one
QLC+ scales every output by - but nothing on the console ever moves it: no VC
widget is bound to it. QLC+ 5 exposes that value to a widget through a Slider
whose SliderMode is GrandMaster rather than the usual Level/Adjust/Submaster,
confirmed to load on the installed 5.2.2 binary by
`tests/probes/probe-gm-slider.qxw` (see docs/qlc5-verification.md).
"""

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state

SLIDER_MODE = "GrandMaster"
VALUE_DISPLAY_STYLE = "Exact"
LOW_LIMIT = 0
HIGH_LIMIT = 255
DEFAULT_VALUE = 255


def build_grand_master_slider(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
) -> etree._Element:
    """Append a GrandMaster <Slider> to parent and return it."""
    slider = etree.SubElement(parent, f"{{{QLC_NS}}}Slider")
    slider.set("Caption", caption)
    slider.set("ID", str(widget_id))
    slider.set("WidgetStyle", "Slider")
    slider.set("InvertedAppearance", "false")

    build_window_state(slider, x, y, width, height)
    build_appearance(slider)

    mode = etree.SubElement(slider, f"{{{QLC_NS}}}SliderMode")
    mode.set("ValueDisplayStyle", VALUE_DISPLAY_STYLE)
    mode.text = SLIDER_MODE

    level = etree.SubElement(slider, f"{{{QLC_NS}}}Level")
    level.set("LowLimit", str(LOW_LIMIT))
    level.set("HighLimit", str(HIGH_LIMIT))
    level.set("Value", str(DEFAULT_VALUE))

    return slider
