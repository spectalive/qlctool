"""Whether a colour has enough chroma to fight: below half, it is a pastel with no hue to lose."""

SATURATED_FROM = 0.5


def saturated(colour: tuple[int, int, int]) -> bool:
    top = max(colour)
    return top > 0 and (top - min(colour)) / top >= SATURATED_FROM
