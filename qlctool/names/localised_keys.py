"""An identifier-keyed table, keyed instead by the show's display names (ruling B4)."""

from collections.abc import Mapping
from typing import TypeVar

from .names import Names

T = TypeVar("T")


def localised_keys(table: Mapping[str, T], names: Names) -> dict[str, T]:
    """Same values, each key replaced by `names.display(key)`, order kept."""
    return {names.display(identifier): value for identifier, value in table.items()}
