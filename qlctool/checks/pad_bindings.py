"""Every input channel of the pad's universe a console widget listens on, and who listens."""

from lxml import etree

from ..pad_input_universe import pad_input_universe
from ..xmlutil import localname
from .bound_inputs import bound_inputs


def pad_bindings(root: etree._Element) -> dict[int, list[str]]:
    """Channel -> captions of the widgets bound to it on the pad's input universe."""
    bindings: dict[int, list[str]] = {}
    for channel, element in bound_inputs(root, pad_input_universe(root)):
        caption = element.attrib.get("Caption") or localname(element)
        bindings.setdefault(channel, []).append(caption)
    return bindings
