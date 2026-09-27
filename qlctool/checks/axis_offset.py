"""The Offset of a named Axis under an EFX, or None when the axis is absent."""

from lxml import etree

from ..findall_local import findall_local
from .function_number import function_number


def axis_offset(function: etree._Element, name: str) -> int | None:
    for axis in findall_local(function, "Axis"):
        if axis.attrib.get("Name") != name:
            continue
        return function_number(axis, "Offset")
    return None
