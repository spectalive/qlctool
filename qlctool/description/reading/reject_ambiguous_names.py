"""An override may not spell a name another identifier already answers to."""

from collections.abc import Mapping
from dataclasses import replace

from ...names.default_names import default_names
from ...names.sections import SECTIONS


def reject_ambiguous_names(overrides: Mapping[str, Mapping[str, str]], where: str) -> None:
    """Raise when an override's word is another identifier, or one of its spellings.

    `Names.identify` accepts every spelling in every catalogue, so `[names.en]
    blue = "red"` would make "red" name two colours and fail the build later.
    """
    names = replace(default_names(), overrides=overrides)
    for language, entries in overrides.items():
        for identifier, word in entries.items():
            sections = [s for s in SECTIONS if identifier in names.identifiers(s)]
            others = [m for m in names.lookup(word, sections) if m != identifier]
            if others:
                raise ValueError(
                    f"{where}: [names.{language}] {identifier} = {word!r} is already a name "
                    f"of {', '.join(others)}: one word may name only one thing"
                )
