"""[names.<lang>]: the show's own words for catalogue identifiers."""

from collections.abc import Mapping
from difflib import get_close_matches
from typing import Any

from ...names.check_override_fields import check_override_fields
from ...names.default_names import default_names
from ...names.sections import SECTIONS
from ...names.shipped_languages import shipped_languages
from .reject_ambiguous_names import reject_ambiguous_names


def read_names(table: Mapping[str, Any], where: str) -> dict[str, dict[str, str]]:
    """Language -> identifier -> word, every identifier one the catalogues know."""
    known = sorted({i for section in SECTIONS for i in default_names().identifiers(section)})
    overrides: dict[str, dict[str, str]] = {}
    for language, entries in table.items():
        here = f"{where}: [names.{language}]"
        if language not in shipped_languages():
            raise ValueError(f"{here} is not a shipped language: {', '.join(shipped_languages())}")
        if not isinstance(entries, dict):
            raise ValueError(f'{here} must be a table of identifier = "word"')
        for identifier, text in entries.items():
            if identifier not in known:
                close = get_close_matches(identifier, known, n=3)
                hint = f"; did you mean {', '.join(close)}?" if close else ""
                raise ValueError(f"{here} {identifier!r} is not a catalogue identifier{hint}")
            if not isinstance(text, str) or not text:
                raise ValueError(f"{here} {identifier} must be a non-empty string")
        overrides[language] = dict(entries)
    reject_ambiguous_names(overrides, where)
    check_override_fields(overrides, where)
    return overrides
