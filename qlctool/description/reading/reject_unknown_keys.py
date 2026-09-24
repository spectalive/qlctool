"""Refuse a key a section does not define - a typo must not become a silent default."""

from collections.abc import Iterable, Mapping
from typing import Any


def reject_unknown_keys(table: Mapping[str, Any], allowed: Iterable[str], where: str) -> None:
    """Raise listing the unknown keys and the allowed ones."""
    known = set(allowed)
    unknown = sorted(set(table) - known)
    if unknown:
        raise ValueError(
            f"{where}: unknown key(s) {', '.join(unknown)}; allowed: {', '.join(sorted(known))}"
        )
