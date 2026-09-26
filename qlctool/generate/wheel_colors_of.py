"""Every colour a wheel step can put the room on."""

from collections.abc import Mapping, Sequence


def wheel_colors_of(
    wheel: Mapping[str, tuple[int, int, int]], contrasts: Sequence[tuple[str, str]]
) -> dict[str, tuple[int, int, int]]:
    """Every colour a wheel step can put the room on, in wheel order.

    The solid steps use the primary palette; a contrast step puts everything
    that is not a moving head - the pixel groups included - on its *rest*
    colour, so those are wheel colours too even when the primaries skip them.
    """
    # Every wheel colour since 2026-09-22: the full automatic mode runs all
    # seventeen, so the pixel groups need a matrix for each of them. Never
    # white - no rotation steps it (`wheel_palette`).
    names = list(wheel)
    names += [rest for _, rest in contrasts if rest not in names]
    return {name: wheel[name] for name in names}
