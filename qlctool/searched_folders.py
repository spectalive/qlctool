"""The folders a library searched, said the way a message can print them."""

from .checks.rendered_value import rendered_value
from .checks.searched_folders_said import searched_folders_said
from .library import FixtureLibrary
from .names.names import Names


def searched_folders(library: FixtureLibrary, names: Names) -> str:
    """The library's folders, comma-separated, or the catalogue's word for none."""
    return str(rendered_value(names, searched_folders_said(library)))
