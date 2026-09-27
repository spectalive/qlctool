"""Whether a channel is doing something: unknown counts as doing something."""


def lit(value: int | None) -> bool:
    return value is None or value > 0
