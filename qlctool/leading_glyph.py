"""Split a caption into the glyph it starts with and the words after it.

The console carries each control's glyph inside its caption (`control_glyph`),
because QLC+'s own `<Icon>` is a path into one machine's disk. The tablet desk
does not have that problem: it draws its own tiles, and a glyph it is handed as
a field can be sized and placed like an icon instead of riding along as the
first character of a label. So the map splits what the console joined.
"""

from .control_glyph import GLYPHS
from .pick_marks import PICK_MARKS

MARKS = frozenset(GLYPHS.values()) | PICK_MARKS


def leading_glyph(caption: str) -> tuple[str, str]:
    """(glyph, rest). The glyph is "" and rest the caption when there is none."""
    head = caption[:1]
    if head in MARKS:
        return head, caption[1:].strip()
    return "", caption
