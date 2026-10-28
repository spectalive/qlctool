"""Every input channel of the OSC universe a console widget listens on, and who listens."""

from lxml import etree

from ..findall_local import findall_local
from ..localname import localname
from .bound_widgets import BOUND_WIDGETS


def osc_bindings(root: etree._Element, universe: int) -> dict[int, list[str]]:
    """Channel -> the widget controls bound to it on `universe`, in document order.

    A control is the widget's caption, with the input id after it for any
    control but the primary one, so a speed dial's 2x reads apart from its wheel.
    """
    bindings: dict[int, list[str]] = {}
    for widget in root.iter():
        if localname(widget) not in BOUND_WIDGETS:
            continue
        caption = widget.get("Caption") or localname(widget)
        for source in findall_local(widget, "Input"):
            if "Channel" not in source.attrib or int(source.get("Universe", "0")) != universe:
                continue
            control = source.get("ID", "0")
            label = caption if control == "0" else f"{caption} ({control})"
            bindings.setdefault(int(source.attrib["Channel"]), []).append(label)
    return bindings
