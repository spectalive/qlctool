"""An XML element's stripped text, or the empty string when it has none."""

from lxml import etree


def text_of(element: etree._Element | None) -> str:
    return (element.text or "").strip() if element is not None else ""
