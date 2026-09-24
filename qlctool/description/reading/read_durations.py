"""One of [timing]'s duration tables, stated whole: it replaces the default, it does not patch it."""

from collections.abc import Mapping
from typing import Any

from .milliseconds import milliseconds
from .reject_unknown_keys import reject_unknown_keys


def read_durations(
    table: Mapping[str, Any], fields: Mapping[str, str], where: str
) -> dict[str, int]:
    """ShowTiming field -> milliseconds, for every key of `fields`, all of which must be given.

    `levels = { party_s = 600 }` alone would keep three lengths nobody wrote in
    the file; a stated table is the whole table (F7), so a missing key is refused.
    """
    reject_unknown_keys(table, fields, where)
    missing = [key for key in fields if key not in table]
    if missing:
        raise ValueError(
            f"{where}: missing {', '.join(missing)}; a stated table gives every one of "
            f"{', '.join(fields)}"
        )
    return {field: milliseconds(table[key], f"{where}.{key}") for key, field in fields.items()}
