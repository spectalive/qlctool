"""What one Scene or Sequence function writes: its FixtureVal channels, verbatim."""

from lxml import etree

from ..findall_local import findall_local


def scene_driven(function: etree._Element) -> dict[int, dict[int, int | None]]:
    driven: dict[int, dict[int, int | None]] = {}
    for value in findall_local(function, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        numbers = [int(n) for n in (value.text or "").split(",") if n != ""]
        driven[fixture_id] = dict(zip(numbers[0::2], numbers[1::2], strict=True))
    return driven
