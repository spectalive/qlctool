"""An axis's (Frequency, Phase in degrees), defaulted and clamped like QLC+.

An EFX with no `<Axis>` of that name keeps the constructor's values (the
arguments); an `<Axis>` that omits a tag reads it as 0, which is what
`EFX::loadXMLAxis` does (`efx.cpp` 1080-1110).
"""

from lxml import etree

from ..xmlutil import findall_local
from .function_number import function_number


def axis_shape(function: etree._Element, name: str, frequency: int, phase: int) -> tuple[int, int]:
    for axis in findall_local(function, "Axis"):
        if axis.attrib.get("Name") != name:
            continue
        frequency = function_number(axis, "Frequency") or 0
        phase = function_number(axis, "Phase") or 0
        break
    return min(max(frequency, 0), 32), min(max(phase, 0), 359)
