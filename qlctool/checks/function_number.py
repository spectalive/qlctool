"""A numeric child element's value, or None when it is missing or not a number."""

from lxml import etree

from ..xmlutil import find_local


def function_number(function: etree._Element, name: str) -> int | None:
    element = find_local(function, name)
    if element is None:
        return None
    text = (element.text or "").strip()
    if not text.lstrip("-").isdigit():
        return None
    return int(text)
