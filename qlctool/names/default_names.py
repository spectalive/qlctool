"""The vocabulary a check or the desk reads a saved workspace with."""

from functools import cache

from .names import Names
from .shipped_names import shipped_names


@cache
def default_names() -> Names:
    """Every shipped catalogue, in Spanish, with no overrides - built once."""
    return shipped_names()
