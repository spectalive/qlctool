"""A description in the words the generator writes: the show language's display names."""

from ..names.names import Names
from .rename_description import rename_description
from .show_description import ShowDescription


def localize_description(description: ShowDescription, names: Names) -> ShowDescription:
    """Every name - an identifier or any spelling - replaced by its display name.

    Accepting any spelling makes this safe on a description built in code with
    display names (the tests do) as well as on an identified one.
    """
    return rename_description(
        description,
        colour=lambda name: names.display(names.identify(name, ("colors",))),
        function=lambda name: names.display(names.identify(name, ("functions",))),
    )
