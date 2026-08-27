"""Build a Virtual Console <Slider> in Level mode over specific channels.

A Level slider writes one DMX value straight onto the channels it lists, HTP
against whatever else drives them - which is how the hand-built console's
"Strobo LED Effect Speed" fader set the panels' speed live while the effect
chaser picked which programme ran. The XML shape is copied from that widget
(DeluxeEventos2, Slider ID 130) and loads unchanged in QLC+ 5.
"""

from collections.abc import Sequence

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state

# VCSlider treats this function id as "none" on the playback side.
NO_PLAYBACK = 4294967295


def build_level_slider(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
    channels: Sequence[tuple[int, int]],
    value: int = 0,
) -> etree._Element:
    """channels is one (fixture id, channel offset) per channel the fader owns."""
    slider = etree.SubElement(parent, f"{{{QLC_NS}}}Slider")
    slider.set("Caption", caption)
    slider.set("ID", str(widget_id))
    slider.set("WidgetStyle", "Slider")
    slider.set("InvertedAppearance", "false")
    slider.set("CatchValues", "true")

    build_window_state(slider, x, y, width, height)
    build_appearance(slider, frame_style="Sunken")

    mode = etree.SubElement(slider, f"{{{QLC_NS}}}SliderMode")
    mode.set("ValueDisplayStyle", "Exact")
    mode.set("ClickAndGoType", "None")
    mode.set("Monitor", "true")
    mode.text = "Level"

    level = etree.SubElement(slider, f"{{{QLC_NS}}}Level")
    level.set("LowLimit", "0")
    level.set("HighLimit", "255")
    level.set("Value", str(value))
    for fixture_id, offset in channels:
        channel = etree.SubElement(level, f"{{{QLC_NS}}}Channel")
        channel.set("Fixture", str(fixture_id))
        channel.text = str(offset)

    playback = etree.SubElement(slider, f"{{{QLC_NS}}}Playback")
    function = etree.SubElement(playback, f"{{{QLC_NS}}}Function")
    function.text = str(NO_PLAYBACK)

    return slider
