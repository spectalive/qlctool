"""A list said in the workspace's language: the parts, and what goes between them."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Joined:
    """`parts` rendered and joined by `separator`; either may hold a `Phrase`.

    "«A» y «B»" is `Joined(("«A»", "«B»"), Phrase("list_and"))`: the "y" is the
    catalogue's, so an English show reads "«A» and «B»".
    """

    parts: tuple[object, ...]
    separator: object
