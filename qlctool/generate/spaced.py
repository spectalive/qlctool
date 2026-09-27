"""A stable, evenly distributed subset of `count` items, without repeats."""

from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def spaced(items: Sequence[T], count: int) -> list[T]:
    if len(items) <= count:
        return list(items)
    return [items[round(i * (len(items) - 1) / (count - 1))] for i in range(count)]
