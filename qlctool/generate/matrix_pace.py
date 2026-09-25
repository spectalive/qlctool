"""How fast one RGBMatrix runs, so a chaser can hold it for one full pass."""

from ..matrix_step_count import matrix_step_count


def matrix_pace(
    algorithm: str | None, width: int, height: int, duration: int, cap: int
) -> tuple[int, int]:
    """Frame length and full-pass length for one algorithm on one grid.

    A pass longer than the cap is run faster rather than cut off: a wave across
    fifteen PARs at the nominal frame rate would hold one colour for ten
    seconds, and holding it is as wrong as cutting it.
    """
    count = matrix_step_count(algorithm, width, height)
    frame_ms = duration
    if duration * count > cap:
        frame_ms = max(1, cap // count)
    return frame_ms, frame_ms * count
