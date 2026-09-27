"""A fixture group's stripped `<Name>` text, or the empty string when it has none."""

from lxml import etree

from ..xmlutil import find_local


def group_name(group: etree._Element) -> str:
    name = find_local(group, "Name")
    return (name.text or "").strip() if name is not None else ""
