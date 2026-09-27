"""Every text a catalogue identifier has in any shipped language."""

from functools import cache

from ..names.load_catalogue import load_catalogue
from ..names.shipped_languages import shipped_languages


@cache
def catalogue_spellings(identifier: str) -> tuple[str, ...]:
    """The identifier's text in each shipped catalogue, without repeats."""
    found: list[str] = []
    for language in shipped_languages():
        for section in load_catalogue(language).values():
            text = section.get(identifier)
            if text is not None and text not in found:
                found.append(text)
    return tuple(found)
