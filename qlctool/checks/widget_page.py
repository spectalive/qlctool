"""Which page of the multipage console a widget sits on."""

from lxml import etree


def widget_page(widget: etree._Element) -> str:
    """The `Page` of the nearest widget up the tree that carries one; "0" when none does."""
    current: etree._Element | None = widget
    while current is not None:
        page = current.get("Page")
        if page is not None:
            return page
        current = current.getparent()
    return "0"
