"""A show's colours: the palette and every subset and pairing drawn from it."""

from collections.abc import Mapping
from dataclasses import dataclass

from ..argb import RGB
from ..color_pair import ColorPair


@dataclass(frozen=True)
class ColourSettings:
    """The palette, which of its colours each mode uses, and which pairs go together.

    `white` is the palette entry no automatic rotation steps (`wheel_palette`);
    `analogous_pairs` and `key_split_pairs` build the per-group splits,
    `complementary_pairs` the heads-against-the-rest contrasts.
    """

    palette: Mapping[str, RGB]
    primary: tuple[str, ...]
    simple: tuple[str, ...]
    white: str
    analogous_pairs: tuple[ColorPair, ...]
    key_split_pairs: tuple[tuple[str, str], ...]
    complementary_pairs: tuple[ColorPair, ...]
    matrix_colors: tuple[str, ...]
