"""Semantic equality for QLC+ XML trees.

QLC+ ignores insignificant whitespace when it loads a workspace, so the round
trip we must guarantee is *semantic*: same elements, same attributes, same text,
same order - not byte-for-byte. This is the master safety net that lets the
toolkit rewrite a show without corrupting it.
"""

from lxml import etree

from .difference_at import difference_at


def semantic_equal(a: etree._Element, b: etree._Element) -> bool:
    """True when two elements are equivalent as far as QLC+ cares.

    Compares local tag name, attribute set, stripped text and tail, and children
    in document order. Whitespace-only text and namespace prefixes are ignored.
    """
    return difference_at(a, b, path="") is None
