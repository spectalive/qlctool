"""A list a description gives under a key, refused when it is not a list."""

from collections.abc import Mapping
from typing import Any


def list_at(parent: Mapping[str, Any], key: str, where: str) -> list[Any]:
    """`parent[key]` as a list, or an empty one when the key is not there."""
    value = parent.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{where}: {key} must be a list, got {value!r}")
    return value
