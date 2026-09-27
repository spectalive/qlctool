"""Whether an AudioTriggers spectrum bar actually targets something."""

from lxml import etree

from ..xmlutil import find_local
from .spectrum_bar_types import DMX_BAR, FUNCTION_BAR, WIDGET_BAR


def spectrum_bar_is_bound(bar: etree._Element, widgets_by_id: dict[str, etree._Element]) -> bool:
    """Whether this bar actually targets a channel, a function or a widget."""
    bar_type = bar.attrib.get("Type")
    if bar_type == FUNCTION_BAR:
        return bar.attrib.get("FunctionID") is not None
    if bar_type == WIDGET_BAR:
        widget_id = bar.attrib.get("WidgetID")
        # A WidgetID with no matching widget is a dangling reference, not a
        # binding: QLC+'s own `checkWidgetFunctionality` looks the widget up
        # by ID and does nothing when that lookup fails, so a bar left
        # pointing at a deleted or never-created widget presses nothing -
        # the same as no WidgetID at all.
        return widget_id is not None and widget_id in widgets_by_id
    if bar_type == DMX_BAR:
        channels = find_local(bar, "DMXChannels")
        return channels is not None and bool((channels.text or "").strip())
    return False
