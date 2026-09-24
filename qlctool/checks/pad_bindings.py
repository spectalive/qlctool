"""Every input channel a console widget listens on, and the widgets listening on it."""

from lxml import etree

from ..xmlutil import findall_local, localname
from .bound_widgets import BOUND_WIDGETS


def pad_bindings(root: etree._Element) -> dict[int, list[str]]:
    """Channel -> captions of the widgets bound to it. Key-only `<Input>`s bind a keyboard, not a pad."""
    bindings: dict[int, list[str]] = {}
    for element in root.iter():
        if localname(element) not in BOUND_WIDGETS:
            continue
        caption = element.attrib.get("Caption") or localname(element)
        for source in findall_local(element, "Input"):
            if "Channel" not in source.attrib:
                continue
            bindings.setdefault(int(source.attrib["Channel"]), []).append(caption)
    return bindings
