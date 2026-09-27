"""Write one decomposed XML element to its own fragment file."""

from pathlib import Path

from lxml import etree

from .constants import XML_DECLARATION


def write_fragment(path: Path, element: etree._Element) -> None:
    body = etree.tostring(element, pretty_print=True, encoding="unicode")
    header = f"{XML_DECLARATION}\n"
    path.write_text(header + body, encoding="utf-8")
