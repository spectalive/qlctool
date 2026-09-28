"""The (offset, value) pairs a FixtureVal element carries."""


def fixture_val_pairs(value):
    numbers = [int(n) for n in (value.text or "").split(",") if n != ""]
    return dict(zip(numbers[0::2], numbers[1::2], strict=True))
