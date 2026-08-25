"""Build a Virtual Console <AudioTriggers> that fires widgets off the music.

The widget splits the input spectrum into bars; a bar whose level crosses its
threshold presses the Virtual Console widget it is bound to. It stays off until
somebody enables it, and it needs an audio input picked in QLC+'s
Configuration, so it is inert rather than dangerous on a show laptop with no
input selected.
"""

from collections.abc import Sequence

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state

# AudioBar::BarType - 3 presses another Virtual Console widget.
BAR_TYPE_WIDGET = 3


def build_audio_triggers(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
    bars: Sequence[tuple[str, int | None]],
    key: str | None = None,
) -> etree._Element:
    """bars is one (name, widget id to press) per spectrum band; None = unbound."""
    triggers = etree.SubElement(parent, f"{{{QLC_NS}}}AudioTriggers")
    triggers.set("BarsNumber", str(len(bars)))
    triggers.set("Caption", caption)
    triggers.set("ID", str(widget_id))

    build_window_state(triggers, x, y, width, height)
    build_appearance(triggers, frame_style="Sunken")
    if key is not None:
        etree.SubElement(triggers, f"{{{QLC_NS}}}Key").text = key

    for index, (name, target_id) in enumerate(bars):
        if target_id is None:
            continue
        bar = etree.SubElement(triggers, f"{{{QLC_NS}}}SpectrumBar")
        bar.set("Name", name)
        bar.set("Type", str(BAR_TYPE_WIDGET))
        bar.set("MinThreshold", "12")
        bar.set("MaxThreshold", "51")
        bar.set("Divisor", "1")
        bar.set("Index", str(index))
        bar.set("WidgetID", str(target_id))

    return triggers
