"""Find every QLC+ XML child by local name, ignoring its namespace."""

from lxml import etree


def findall_local(parent: etree._Element, name: str) -> list[etree._Element]:
    return parent.findall(f"{{*}}{name}")
