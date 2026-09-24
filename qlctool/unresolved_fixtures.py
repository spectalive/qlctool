"""Patched fixtures the library has no definition for."""

from lxml import etree

from .fixture import patched_fixtures
from .library import FixtureLibrary


def unresolved_fixtures(root: etree._Element, library: FixtureLibrary) -> list[str]:
    """ "Manufacturer Model" of every patched fixture with no definition, without repeats."""
    missing: dict[str, None] = {}
    for fixture in patched_fixtures(root):
        if library.get(fixture.manufacturer, fixture.model) is None:
            missing[f"{fixture.manufacturer} {fixture.model}"] = None
    return list(missing)
