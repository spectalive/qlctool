"""Build the <Input> external-control binding of a Virtual Console widget.

QLC+ stores a widget's external input as `<Input ID Universe Channel>`
(qmlui/virtualconsole/vcwidget.cpp, VCWidget::loadXMLInputSource). ID names
which of the widget's controls the source drives; 0 is the primary one on
every widget this console generates - a button's Pressure, a slider's Slider
Control, a speed dial's Time wheel, a frame's Next Page - and a frame's
Previous Page is 1 (qmlui/virtualconsole/vcframe.h).
"""

from lxml import etree

from ..constants import QLC_NS


def build_input_source(
    widget: etree._Element, channel: int, universe: int = 0, source_id: int = 0
) -> etree._Element:
    """Append an <Input> binding to widget and return it."""
    source = etree.SubElement(widget, f"{{{QLC_NS}}}Input")
    source.set("ID", str(source_id))
    source.set("Universe", str(universe))
    source.set("Channel", str(channel))
    return source
