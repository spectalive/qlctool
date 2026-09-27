"""A QLC+ XML element's local name, stripped of its namespace.

Both .qxw and .qxf put every element in the QLC+ namespace. Working by local
name keeps the rest of the toolkit free of namespace bookkeeping.
"""

from lxml import etree


def localname(element: etree._Element) -> str:
    # A comment or a processing instruction carries a callable, not a name.
    tag: object = element.tag
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]
