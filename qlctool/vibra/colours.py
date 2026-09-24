"""The Vibra show's colours, from the tables its owner's choices are recorded in."""

from ..analogous_pairs import ANALOGOUS_PAIRS
from ..complementary_pairs import COMPLEMENTARY_PAIRS
from ..description.colour_settings import ColourSettings
from ..key_split_pairs import KEY_SPLIT_PAIRS
from ..palette import PALETTE, PRIMARY_COLORS
from ..simple_colors import SIMPLE_COLORS
from ..wheel_palette import WHITE
from .matrix_colors import MATRIX_COLORS

VIBRA_COLOURS = ColourSettings(
    palette=PALETTE,
    primary=PRIMARY_COLORS,
    simple=SIMPLE_COLORS,
    white=WHITE,
    analogous_pairs=ANALOGOUS_PAIRS,
    key_split_pairs=KEY_SPLIT_PAIRS,
    complementary_pairs=COMPLEMENTARY_PAIRS,
    matrix_colors=MATRIX_COLORS,
)
