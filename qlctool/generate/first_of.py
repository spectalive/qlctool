"""The first of a generated list, or None."""

from collections.abc import Sequence


def first_of(ids: Sequence[int]) -> int | None:
    """The first of a generated list, or None when nothing was generated.

    A wheel's first position is its open one in every definition here, which is
    what the quiet level wants: no gobo rather than whatever was left in.
    """
    return ids[0] if ids else None
