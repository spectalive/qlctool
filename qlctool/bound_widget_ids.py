"""Every input channel a console widget listens on, and the ids of those widgets."""

from lxml import etree

from .checks.bound_widgets import BOUND_WIDGETS
from .xmlutil import findall_local, localname


def bound_widget_ids(root: etree._Element) -> dict[int, list[int]]:
    """Channel -> ids of the widgets bound to it, in document order.

    Key-only `<Input>`s bind a keyboard, not a pad, as in `pad_bindings`.
    """
    bindings: dict[int, list[int]] = {}
    for element in root.iter():
        if localname(element) not in BOUND_WIDGETS or "ID" not in element.attrib:
            continue
        for source in findall_local(element, "Input"):
            if "Channel" in source.attrib:
                bindings.setdefault(int(source.attrib["Channel"]), []).append(
                    int(element.attrib["ID"])
                )
    return bindings
