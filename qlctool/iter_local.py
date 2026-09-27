"""Walk every QLC+ XML descendant by local name, ignoring its namespace."""

from collections.abc import Iterator

from lxml import etree


def iter_local(root: etree._Element, name: str) -> Iterator[etree._Element]:
    yield from root.iter(f"{{*}}{name}")
