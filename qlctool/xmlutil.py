"""Namespace-agnostic helpers for reading QLC+ XML.

Both .qxw and .qxf put every element in the QLC+ namespace. Working by local
name keeps the rest of the toolkit free of namespace bookkeeping.
"""

from lxml import etree


def localname(element: etree._Element) -> str:
    tag = element.tag
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def find_local(parent: etree._Element, name: str) -> etree._Element | None:
    for child in parent:
        if localname(child) == name:
            return child
    return None


def findall_local(parent: etree._Element, name: str) -> list[etree._Element]:
    return [child for child in parent if localname(child) == name]


def iter_local(root: etree._Element, name: str):
    for element in root.iter():
        if localname(element) == name:
            yield element
