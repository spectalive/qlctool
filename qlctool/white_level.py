"""What a fixture's dedicated white emitter gets when a look asks for (r, g, b).

Every white look in this show was RGB-mixed white: red, green and blue at 255
and the White channel of the two Mini Led heads and the three rings of each
MAC WASH left at zero - a patched emitter no look ever used (Codex, cross-audit
2026-09-02). The white LED is the brightest and truest white the fixture has,
so a look that means white should use it, and a colour that means red should
say zero to it rather than leave it to whatever ran before.

The share of white in a colour is the part red, green and blue have in common:
the minimum of the three. That is the standard RGB-to-RGBW split, it leaves the
hue untouched, and it is exactly zero for a saturated colour.
"""

RGB = tuple[int, int, int]


def white_level(rgb: RGB) -> int:
    """The dedicated white channel's value for an (r, g, b) request."""
    return min(rgb)
