"""The biggest figure that still fits its window once QLC+ turns it.

A figure's Width and Height are its reach only at Rotation 0: QLC+ turns the
scaled shape (`efx_extent`), so the beams' Diamond, Leaf and Circle, drawn at
the window's own half-size and turned 90 or 45 degrees, reached past the
window on tilt - Diamante put the 7R at tilt 200-240 over a 207-234 window
(en-sala DMX re-audit, 2026-09-27). The turned figure is sized by what it
reaches, not by what it is called.
"""

from functools import cache

from ..efx_extent import efx_extent

# Float noise on a reach drawn exactly to the edge is still inside.
_TOLERANCE = 1e-6


@cache
def fit_rotated_figure(
    algorithm: str, rotation: int, pan_span: int, tilt_span: int
) -> tuple[int, int]:
    """The largest-area integer (width, height) whose turned reach fits the spans.

    Each side is at most twice its span, and the figure fits when its sampled
    reach stays within +-pan_span on pan and +-tilt_span on tilt. Ties go to
    the wider figure. Cached: a search samples the figure a thousand times,
    and every show generated in a process asks the same few questions.

    The search stops at the first height that fits under each width, which
    is the largest only because the reach grows with each side: every term
    of `rotateAndScale` scales with Width or Height, so shrinking a side
    never pushes a point further out. That holds for every algorithm and
    rotation, and was also checked by brute force over 10-350 degrees.
    """

    def fits(width: int, height: int) -> bool:
        (pan_min, pan_max), (tilt_min, tilt_max) = efx_extent(algorithm, width, height, rotation)
        return (
            -pan_span - _TOLERANCE <= pan_min
            and pan_max <= pan_span + _TOLERANCE
            and -tilt_span - _TOLERANCE <= tilt_min
            and tilt_max <= tilt_span + _TOLERANCE
        )

    best = (0, 0)
    for width in range(pan_span * 2, -1, -1):
        if width * tilt_span * 2 < best[0] * best[1]:
            break
        for height in range(tilt_span * 2, -1, -1):
            if width * height < best[0] * best[1]:
                break
            if fits(width, height):
                if width * height > best[0] * best[1]:
                    best = (width, height)
                break
    return best
