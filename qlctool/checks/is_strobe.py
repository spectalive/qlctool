"""Whether a function is an RGBMatrix run with the Strobe algorithm."""

from lxml import etree

from ..find_local import find_local

STROBE = "Strobe"


def is_strobe(function: etree._Element) -> bool:
    if function.attrib.get("Type") != "RGBMatrix":
        return False
    algorithm = find_local(function, "Algorithm")
    return algorithm is not None and (algorithm.text or "").strip() == STROBE
