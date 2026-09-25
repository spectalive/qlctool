"""The function ids one element of an engine function writes."""

from collections.abc import Iterator

from lxml import etree

from ..xmlutil import localname
from .invalid_function_id import INVALID_ID

STEP_TYPES = ("Chaser", "Collection")


def engine_reference(
    function: etree._Element, element: etree._Element, holder: str
) -> Iterator[tuple[str, str]]:
    """(holder, the raw id) for each reference `element` of `function` makes."""
    tag = localname(element)
    if element is function:
        if function.get("Type") == "Sequence" and "BoundScene" in function.attrib:
            yield holder, function.get("BoundScene", "")
    elif tag == "Step" and function.get("Type") in STEP_TYPES:
        yield holder, (element.text or "").strip()
    elif tag == "ShowFunction":
        yield holder, element.get("ID", "")
    elif tag == "Track" and element.get("SceneID", INVALID_ID) != INVALID_ID:
        yield holder, element.get("SceneID", "")
