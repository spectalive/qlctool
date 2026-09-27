"""Write one EFX axis child element (Offset, Frequency, Phase)."""

from lxml import etree

from ..constants import QLC_NS
from .child import child
from .efx_axis import EFXAxis


def axis(parent: etree._Element, name: str, axis: EFXAxis) -> None:
    element = etree.SubElement(parent, f"{{{QLC_NS}}}Axis")
    element.set("Name", name)
    child(element, "Offset", axis.offset)
    child(element, "Frequency", axis.frequency)
    child(element, "Phase", axis.phase)
