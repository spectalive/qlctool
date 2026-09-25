"""The folders a library searched, said the way a message can print them."""

from .library import FixtureLibrary
from .names.names import Names


def searched_folders(library: FixtureLibrary, names: Names) -> str:
    """The library's folders, comma-separated, or the catalogue's word for none."""
    return ", ".join(str(folder) for folder in library.sources) or names.display(
        "searched_no_folder"
    )
