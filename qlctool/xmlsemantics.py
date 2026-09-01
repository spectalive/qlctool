"""Semantic equality for QLC+ XML trees.

QLC+ ignores insignificant whitespace when it loads a workspace, so the round
trip we must guarantee is *semantic*: same elements, same attributes, same text,
same order - not byte-for-byte. This is the master safety net that lets the
toolkit rewrite a show without corrupting it.
"""

from lxml import etree


def _localname(tag: object) -> str:
    """Strip the namespace from a tag, so comparison ignores prefix bindings."""
    if not isinstance(tag, str):
        # Comments / processing instructions compare by their callable tag.
        return str(tag)
    return tag.rsplit("}", 1)[-1]


def _text(value: str | None) -> str:
    return (value or "").strip()


def semantic_equal(a: etree._Element, b: etree._Element) -> bool:
    """True when two elements are equivalent as far as QLC+ cares.

    Compares local tag name, attribute set, stripped text and tail, and children
    in document order. Whitespace-only text and namespace prefixes are ignored.
    """
    return _first_difference(a, b, path="") is None


def first_difference(a: etree._Element, b: etree._Element) -> str | None:
    """Return a human-readable path to the first mismatch, or None if equal.

    Useful in test failures: it points at the exact node that diverged instead
    of dumping two multi-megabyte trees.
    """
    return _first_difference(a, b, path="")


def _first_difference(a: etree._Element, b: etree._Element, path: str) -> str | None:
    here = f"{path}/{_localname(a.tag)}"

    if _localname(a.tag) != _localname(b.tag):
        return f"{here}: tag {_localname(a.tag)!r} != {_localname(b.tag)!r}"

    if dict(a.attrib) != dict(b.attrib):
        return f"{here}: attrs {dict(a.attrib)} != {dict(b.attrib)}"

    if _text(a.text) != _text(b.text):
        return f"{here}: text {_text(a.text)!r} != {_text(b.text)!r}"

    ac = list(a)
    bc = list(b)
    if len(ac) != len(bc):
        return f"{here}: child count {len(ac)} != {len(bc)}"

    for ca, cb in zip(ac, bc):
        diff = _first_difference(ca, cb, here)
        if diff is not None:
            return diff

    return None
