"""Put a console widget on one page of its multipage frame.

Moved verbatim out of `live_console` (2026-09-27 split).
"""

from lxml import etree


def on_page(widget: etree._Element, page: int | None) -> None:
    """Which page of a multipage frame this widget belongs to; 0 is implicit."""
    if page:
        widget.set("Page", str(page))
