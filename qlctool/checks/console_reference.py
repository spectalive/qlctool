"""The function id one console element writes, if it writes one."""

from lxml import etree

from ..xmlutil import localname

# Console tags whose text is a function id.
CONSOLE_TEXT_TAGS = ("Chaser", "FuncID")
# Console tags whose attribute is a function id.
CONSOLE_ATTRIBUTES = {"Schedule": "Function", "Adjust": "Function"}
# The audio bars' attribute: a function id on whichever element carries it.
AUDIO_BAR_ATTRIBUTE = "FunctionID"


def console_reference(element: etree._Element) -> str | None:
    """The raw id `element` names, or None when it names no function."""
    tag = localname(element)
    if tag == "Function":
        return element.get("ID", (element.text or "").strip())
    if tag in CONSOLE_TEXT_TAGS:
        return (element.text or "").strip()
    if AUDIO_BAR_ATTRIBUTE in element.attrib:
        return element.get(AUDIO_BAR_ATTRIBUTE)
    attribute = CONSOLE_ATTRIBUTES.get(tag)
    if attribute is not None and attribute in element.attrib:
        return element.get(attribute)
    return None
