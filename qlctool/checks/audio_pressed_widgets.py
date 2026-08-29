"""Widget IDs an AudioTriggers spectrum bar presses instead of a finger.

A button wired to a spectrum bar is worked by the PA, not by the operator.
Every rule about what a hand on the console gets - or must not get - starts
from this same list.
"""

from lxml import etree

from ..xmlutil import iter_local


def audio_pressed_widgets(console: etree._Element) -> set[str]:
    pressed: set[str] = set()
    for triggers in iter_local(console, "AudioTriggers"):
        for bar in iter_local(triggers, "SpectrumBar"):
            widget_id = bar.attrib.get("WidgetID")
            if widget_id is not None:
                pressed.add(widget_id)
    return pressed
