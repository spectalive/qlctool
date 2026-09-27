"""Point at the first path where two QLC+ XML trees stop being equivalent."""

from lxml import etree

from .difference_at import difference_at


def first_difference(a: etree._Element, b: etree._Element) -> str | None:
    """Return a human-readable path to the first mismatch, or None if equal.

    Useful in test failures: it points at the exact node that diverged instead
    of dumping two multi-megabyte trees.
    """
    return difference_at(a, b, path="")
