"""A FixtureVal element's comma-separated text as offset -> level pairs."""

from lxml import etree


def fixture_val_pairs(value: etree._Element) -> dict[int, int]:
    numbers = [int(n) for n in (value.text or "").split(",") if n != ""]
    return dict(zip(numbers[0::2], numbers[1::2], strict=True))
