"""The vocabulary a description is written in and generated with."""

from ..names.names import Names
from ..names.shipped_names import shipped_names
from .show_description import ShowDescription


def description_names(description: ShowDescription) -> Names:
    """The shipped catalogues in the description's language, with its overrides."""
    return shipped_names(description.language, description.names)
