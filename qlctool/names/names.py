"""Identifiers <-> display names, across every shipped language and a show's overrides."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from difflib import get_close_matches

from .name_resolution_error import NameResolutionError


@dataclass(frozen=True)
class Names:
    """One show's vocabulary: its language, every catalogue, and its own overrides.

    `display` answers in the show's language; `lookup` and `identify` accept an
    identifier or any spelling in any catalogue or override, case-insensitively,
    because "rojo", "Rojo" and "red" are the same colour.
    """

    language: str
    catalogues: Mapping[str, Mapping[str, Mapping[str, str]]]
    overrides: Mapping[str, Mapping[str, str]] = field(default_factory=dict)

    def identifiers(self, section: str) -> tuple[str, ...]:
        """The identifiers one section defines, in catalogue order."""
        return tuple(self.catalogues[self.language].get(section, {}))

    def display(self, identifier: str) -> str:
        """The word the show writes for an identifier."""
        override = self.overrides.get(self.language, {}).get(identifier)
        if override is not None:
            return override
        for entries in self.catalogues[self.language].values():
            if identifier in entries:
                return entries[identifier]
        raise NameResolutionError(f"no {self.language!r} name for identifier {identifier!r}")

    def render(self, identifier: str, **fields: object) -> str:
        """The display name with its fields filled: "Golpe {colour}" -> "Golpe Rojo"."""
        return self.display(identifier).format(**fields)

    def spellings(self, identifier: str) -> tuple[str, ...]:
        """Every word any catalogue or override gives an identifier, without repeats."""
        found = [
            entries[identifier]
            for catalogue in self.catalogues.values()
            for entries in catalogue.values()
            if identifier in entries
        ]
        found += [words[identifier] for words in self.overrides.values() if identifier in words]
        return tuple(dict.fromkeys(found))

    def lookup(self, name: str, sections: Sequence[str]) -> tuple[str, ...]:
        """Every identifier in these sections that `name` spells, case-insensitively."""
        wanted = name.strip().casefold()
        return tuple(
            identifier
            for section in sections
            for identifier in self.identifiers(section)
            if wanted == identifier
            or any(wanted == spelling.strip().casefold() for spelling in self.spellings(identifier))
        )

    def identify(self, name: str, sections: Sequence[str]) -> str:
        """The one identifier `name` spells; an error naming the candidates otherwise."""
        matches = self.lookup(name, sections)
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise NameResolutionError(f"{name!r} is ambiguous: it names {', '.join(matches)}")
        known = [
            word
            for section in sections
            for identifier in self.identifiers(section)
            for word in (identifier, *self.spellings(identifier))
        ]
        close = get_close_matches(name, known, n=5)
        hint = f"; did you mean {', '.join(repr(word) for word in close)}?" if close else ""
        raise NameResolutionError(f"unknown name {name!r} among {', '.join(sections)}{hint}")
