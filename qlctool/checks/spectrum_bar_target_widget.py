"""The widget a VCWidgetBar presses, or None for any other bar type."""

from lxml import etree

from .spectrum_bar_types import WIDGET_BAR


def spectrum_bar_target_widget(
    bar: etree._Element, widgets_by_id: dict[str, etree._Element]
) -> etree._Element | None:
    if bar.attrib.get("Type") != WIDGET_BAR:
        return None
    widget_id = bar.attrib.get("WidgetID")
    return widgets_by_id.get(widget_id) if widget_id is not None else None
