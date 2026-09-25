"""The folders a library searched, before anyone knows the language to say them in."""

from ..library import FixtureLibrary
from .phrase import Phrase


def searched_folders_said(library: FixtureLibrary) -> str | Phrase:
    """The library's folders, comma-separated, or the catalogue's word for none."""
    return ", ".join(str(folder) for folder in library.sources) or Phrase("searched_no_folder")
