"""Find the first semantic mismatch between two QLC+ XML elements, if any."""

from lxml import etree

from .stripped_text import stripped_text
from .tag_localname import tag_localname


def difference_at(a: etree._Element, b: etree._Element, path: str) -> str | None:
    here = f"{path}/{tag_localname(a.tag)}"

    if tag_localname(a.tag) != tag_localname(b.tag):
        return f"{here}: tag {tag_localname(a.tag)!r} != {tag_localname(b.tag)!r}"

    if dict(a.attrib.items()) != dict(b.attrib.items()):
        return f"{here}: attrs {dict(a.attrib.items())} != {dict(b.attrib.items())}"

    if stripped_text(a.text) != stripped_text(b.text):
        return f"{here}: text {stripped_text(a.text)!r} != {stripped_text(b.text)!r}"

    ac = list(a)
    bc = list(b)
    if len(ac) != len(bc):
        return f"{here}: child count {len(ac)} != {len(bc)}"

    for ca, cb in zip(ac, bc, strict=True):
        diff = difference_at(ca, cb, here)
        if diff is not None:
            return diff

    return None
