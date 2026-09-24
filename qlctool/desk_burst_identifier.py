"""What a held desk accent is, by identifier: a hit caption or a palette colour."""

from .desk_policy import split_caption
from .leading_glyph import leading_glyph
from .names.names import Names


def desk_burst_identifier(caption: str, names: Names) -> str | None:
    """The identifier the accent's name spells, without its glyph and key hint; None if none or many."""
    _, text = leading_glyph(split_caption(caption)[0])
    matches = names.lookup(text, ("captions", "colors"))
    return matches[0] if len(matches) == 1 else None
