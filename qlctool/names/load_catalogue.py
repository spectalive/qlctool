"""Read one language's catalogue and refuse a malformed one."""

import tomllib
from functools import cache

from .catalogue_dir import CATALOGUE_DIR
from .identifier_pattern import IDENTIFIER_PATTERN
from .sections import SECTIONS


@cache
def load_catalogue(language: str) -> dict[str, dict[str, str]]:
    """Section -> identifier -> display name. Cached: callers must not mutate it."""
    path = CATALOGUE_DIR / f"{language}.toml"
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    for section, entries in document.items():
        if section not in SECTIONS or not isinstance(entries, dict):
            raise ValueError(
                f"{path}: [{section}] is not a catalogue section; sections: {SECTIONS}"
            )
        for identifier, text in entries.items():
            if (
                not IDENTIFIER_PATTERN.fullmatch(identifier)
                or not isinstance(text, str)
                or not text
            ):
                raise ValueError(
                    f"{path}: [{section}] {identifier!r} must be snake_case = a non-empty string"
                )
    return document
