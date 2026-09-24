"""A description whose names are identifiers, whatever language it was written in."""

from ..names.names import Names
from .rename_description import rename_description
from .show_description import ShowDescription


def identify_description(description: ShowDescription, names: Names) -> ShowDescription:
    """Every colour and function name resolved to its catalogue identifier."""
    return rename_description(
        description,
        colour=lambda name: names.identify(name, ("colors",)),
        function=lambda name: names.identify(name, ("functions",)),
    )
