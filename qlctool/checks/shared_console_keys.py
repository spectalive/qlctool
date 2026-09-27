"""Console keys more than one button binds, ignoring the shared colour-bank digits."""

from lxml import etree

from ..find_local import find_local
from ..xmlutil import localname
from .positioned_widgets import positioned_widgets


def shared_console_keys(frame: etree._Element) -> list[tuple[str, list[str]]]:
    """(key, captions) for every key two or more buttons bind."""
    by_key: dict[str, list[str]] = {}
    for widget, _, _ in positioned_widgets(frame):
        if localname(widget) != "Button":
            continue
        key_element = find_local(widget, "Key")
        if key_element is not None and key_element.text:
            by_key.setdefault(key_element.text, []).append(widget.attrib.get("Caption", ""))
    found: list[tuple[str, list[str]]] = []
    for key, captions in sorted(by_key.items()):
        # 1-0 are on every colour bank on purpose: one key, one colour, three
        # groups. Anything else sharing a key fires two different looks.
        if key in "1234567890" or len(captions) == 1:
            continue
        found.append((key, captions))
    return found
