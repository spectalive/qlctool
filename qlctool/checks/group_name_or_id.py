"""A fixture group's own name, or its bare ID when it declares none."""

from lxml import etree

from ..xmlutil import find_local


def group_name_or_id(group: etree._Element) -> str:
    name = find_local(group, "Name")
    return (name.text or "").strip() if name is not None else str(group.attrib["ID"])
