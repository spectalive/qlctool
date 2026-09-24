"""What a per-group mix wheel steps: neighbours both ways round, plus the keys (`split_pairs`)."""

from .colour_settings import ColourSettings


def split_pairs_of(colours: ColourSettings) -> tuple[tuple[str, str], ...]:
    """Analogous pairs lead-first, then bed-first, then the key splits, without repeats."""
    return tuple(
        dict.fromkeys(
            [
                *((pair.lead, pair.bed) for pair in colours.analogous_pairs),
                *((pair.bed, pair.lead) for pair in colours.analogous_pairs),
                *colours.key_split_pairs,
            ]
        )
    )
