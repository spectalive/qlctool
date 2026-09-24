"""The heads-against-the-rest contrasts a rotation steps (`unison_colors.CONTRAST_PAIRS`)."""

from .colour_settings import ColourSettings


def contrast_pairs_of(colours: ColourSettings) -> tuple[tuple[str, str], ...]:
    """(heads, rest) for every complementary pair, the warm lead on the heads."""
    return tuple((pair.lead, pair.bed) for pair in colours.complementary_pairs)
