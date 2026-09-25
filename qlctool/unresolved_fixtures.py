"""Patched fixtures the library has no definition, or no patched mode, for."""

from lxml import etree

from .fixture import patched_fixtures
from .library import FixtureLibrary
from .resolved_definition import resolved_definition


def unresolved_fixtures(root: etree._Element, library: FixtureLibrary) -> list[str]:
    """ "Manufacturer Model" of every patched fixture that does not resolve, without repeats."""
    missing: dict[str, None] = {}
    for fixture in patched_fixtures(root):
        if resolved_definition(fixture, library) is None:
            missing[f"{fixture.manufacturer} {fixture.model}"] = None
    return list(missing)
