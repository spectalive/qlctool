"""Find a QLC+ XML child by local name, ignoring its namespace."""

from lxml import etree


def find_local(parent: etree._Element, name: str) -> etree._Element | None:
    return parent.find(f"{{*}}{name}")
