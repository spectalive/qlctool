"""Patched fixtures the library has no definition, or no patched mode, for."""

from lxml import etree

from .fixture import PatchedFixture, patched_fixtures
from .library import FixtureLibrary
from .resolved_definition import resolved_definition


def unresolved_fixtures(root: etree._Element, library: FixtureLibrary) -> list[PatchedFixture]:
    """The first patched fixture of every model and mode that does not resolve."""
    missing: dict[tuple[str, str, str], PatchedFixture] = {}
    for fixture in patched_fixtures(root):
        if resolved_definition(fixture, library) is None:
            missing.setdefault((fixture.manufacturer, fixture.model, fixture.mode), fixture)
    return list(missing.values())
