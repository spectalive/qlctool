"""The glyph each manual-pick family wears on its tiles.

A page of picks is a wall of identical buttons whose captions are the only
difference, so each family marks its tiles with one glyph: the colour picks, the
pixel matrices, the head movements, the gobo and prism looks. `control_glyph`
carries the glyphs of the named master buttons; these belong to no function name
at all, because a pick's caption is built from the function it fires.

They live in one place because two files need the same set: `play_page` writes
them into the caption, and `leading_glyph` splits them back out for the tablet.
A mark this file does not list rides along as the first character of a label.
"""

PICK_MARKS: frozenset[str] = frozenset({"🎨", "▦", "↔", "✧"})
