"""Look up a workspace's fixture group by ID, or raise when it has none."""

from lxml import etree

from ..xmlutil import iter_local


def group_of(root: etree._Element, group_id: int) -> etree._Element:
    for element in iter_local(root, "FixtureGroup"):
        if element.attrib.get("ID") == str(group_id):
            return element
    raise KeyError(f"no fixture group with ID {group_id}")
