"""The shorter way round the wheel between two hues, 0 to 180 degrees."""

TURN = 360.0


def hue_gap(first: float, second: float) -> float:
    gap = abs(first - second) % TURN
    return min(gap, TURN - gap)
