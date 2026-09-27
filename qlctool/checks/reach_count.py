"""A reach as DMX counts: whole when it is, one decimal when it is not."""


def reach_count(value: float) -> str:
    rounded = round(value, 1)
    return str(int(rounded)) if rounded == int(rounded) else str(rounded)
