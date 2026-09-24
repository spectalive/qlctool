"""One name from a description, resolved to its identifier, with the file in the error."""

from typing import Any

from ...names.name_resolution_error import NameResolutionError
from ...names.names import Names


def named(names: Names, name: Any, section: str, where: str) -> str:
    """The identifier `name` spells in `section`; a ValueError that says where otherwise."""
    if not isinstance(name, str):
        raise ValueError(f"{where}: expected a name, got {name!r}")
    try:
        return names.identify(name, (section,))
    except NameResolutionError as error:
        raise ValueError(f"{where}: {error}") from error
