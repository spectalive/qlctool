"""Whether a speed dial has a control bound to the tap input."""

from lxml import etree

from ..findall_local import findall_local

TAP_CONTROL_ID = "1"


def has_tap_binding(dial: etree._Element) -> bool:
    return any(source.attrib.get("ID") == TAP_CONTROL_ID for source in findall_local(dial, "Input"))
