"""Build the font string QLC+ stores for a Virtual Console widget.

QLC+ writes `QFont::toString()` into `<Font>` and reads it back with
`QFont::fromString()`, so a generated font has to be in that format. The legacy
ten-field form is the one both Qt 5 and Qt 6 parse, which is what a workspace
generated here has to survive being opened by whatever QLC+ build is at the
venue.
"""

DEFAULT_FAMILY = "Sans Serif"
BOLD = 75
NORMAL = 50


def console_font(point_size: int, bold: bool = True, family: str = DEFAULT_FAMILY) -> str:
    """A `QFont::toString()` string: family, size, and weight; the rest default."""
    weight = BOLD if bold else NORMAL
    return f"{family},{point_size},-1,5,{weight},0,0,0,0,0"
