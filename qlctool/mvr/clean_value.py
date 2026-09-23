"""cos(90 degrees) is 6e-17 in floating point; the file says 0."""


def clean_value(value: float) -> float:
    return round(value, 6) + 0.0
