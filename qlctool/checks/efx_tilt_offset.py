"""The centre of an EFX's Y axis, which is the tilt one."""

from lxml import etree

from ..find_local import find_local
from ..findall_local import findall_local


def efx_tilt_offset(function: etree._Element) -> int | None:
    for axis in findall_local(function, "Axis"):
        if axis.attrib.get("Name") != "Y":
            continue
        offset = find_local(axis, "Offset")
        if offset is None:
            return None
        text = (offset.text or "").strip()
        if not text.lstrip("-").isdigit():
            return None
        return int(text)
    return None
