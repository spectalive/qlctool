"""Read a fixture definition's `<Physical>` block into an Optics."""

from lxml import etree

from .find_local import find_local
from .optics import Optics


def optics_of(physical: etree._Element) -> Optics:
    def attr(name: str, key: str, fallback: str = "0") -> float:
        element = find_local(physical, name)
        return float(element.attrib.get(key, fallback)) if element is not None else 0.0

    return Optics(
        lumens=attr("Bulb", "Lumens"),
        degrees_min=attr("Lens", "DegreesMin"),
        degrees_max=attr("Lens", "DegreesMax"),
        pan_max=attr("Focus", "PanMax"),
        tilt_max=attr("Focus", "TiltMax"),
        layout=(int(attr("Layout", "Width", "1")) or 1, int(attr("Layout", "Height", "1")) or 1),
    )
