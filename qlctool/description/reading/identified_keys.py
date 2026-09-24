"""A table's keys resolved to identifiers, refusing two spellings of one name."""

from collections.abc import Iterable

from ...names.names import Names
from .named import named


def identified_keys(keys: Iterable[str], names: Names, section: str, where: str) -> dict[str, str]:
    """Identifier -> the spelling the table used for it, in the table's order.

    "red" and "Rojo" are the same colour, so a table holding both would lose
    one of them without a word; that is a mistake in the file, and said so.
    """
    spelled: dict[str, str] = {}
    for key in keys:
        identifier = named(names, key, section, where)
        if identifier in spelled:
            raise ValueError(
                f"{where}: {spelled[identifier]!r} and {key!r} both name {identifier}; "
                "give each one once"
            )
        spelled[identifier] = key
    return spelled
