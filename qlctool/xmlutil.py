"""Namespace-agnostic helpers for reading QLC+ XML.

Both .qxw and .qxf put every element in the QLC+ namespace. Working by local
name keeps the rest of the toolkit free of namespace bookkeeping.

The lookups go through lxml's `{*}name` wildcard, which matches that local name
in any namespace or none and does the walk in C: one pass of every check called
`localname` 2.7 million times from Python before this (2026-09-22).
"""

from lxml import etree


def localname(element: etree._Element) -> str:
    tag = element.tag
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def find_local(parent: etree._Element, name: str) -> etree._Element | None:
    return parent.find(f"{{*}}{name}")


def findall_local(parent: etree._Element, name: str) -> list[etree._Element]:
    return parent.findall(f"{{*}}{name}")


def iter_local(root: etree._Element, name: str):
    yield from root.iter(f"{{*}}{name}")
