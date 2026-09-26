"""Every console widget bound to an input channel of one universe."""

from lxml import etree

from ..xmlutil import findall_local, localname
from .bound_widgets import BOUND_WIDGETS


def bound_inputs(root: etree._Element, universe: int) -> list[tuple[int, etree._Element]]:
    """(channel, widget) for each `<Input>` on `universe`, in document order.

    Key-only `<Input>`s bind a keyboard, not a surface, and are left out; so is
    a binding on another universe, which is another controller's.
    """
    found: list[tuple[int, etree._Element]] = []
    for element in root.iter():
        if localname(element) not in BOUND_WIDGETS:
            continue
        for source in findall_local(element, "Input"):
            if "Channel" not in source.attrib:
                continue
            if int(source.attrib.get("Universe", universe)) != universe:
                continue
            found.append((int(source.attrib["Channel"]), element))
    return found
