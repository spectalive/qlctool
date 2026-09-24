"""A sub-table of a description, empty when absent, refused when not a table."""

from collections.abc import Mapping
from typing import Any


def table_at(parent: Mapping[str, Any], key: str, where: str) -> Mapping[str, Any]:
    """`parent[key]` as a table, or an empty one when the key is not there."""
    value = parent.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{where}: {key} must be a table")
    return value
