"""The functions under one that carry a duration a dial can write."""

from collections.abc import Mapping

from lxml import etree

from ..xmlutil import findall_local


def timed_parts(
    element: etree._Element, by_id: Mapping[str | None, etree._Element]
) -> list[etree._Element]:
    """The functions under this one that carry a duration a dial can write.

    A Chaser or an EFX answers for itself. A Collection has no speed of its own,
    so what the dial re-times is each of its members - which is the only way to
    tap a look built as "one EFX per fixture family".
    """
    if element.attrib.get("Type") != "Collection":
        return [element]
    parts: list[etree._Element] = []
    for step in findall_local(element, "Step"):
        member = by_id.get((step.text or "").strip())
        if member is not None and member.attrib.get("Type") in ("EFX", "Chaser"):
            parts.append(member)
    return parts
