"""Resolve capabilities for every patched fixture in a workspace.

The convenience join generators start from: workspace + library -> one
FixtureCapabilities per fixture whose model the library knows. Fixtures with no
matching definition (e.g. Generic) are skipped, because their channel roles
cannot be resolved and a generator must not guess at them.
"""

from lxml import etree

from .capability import FixtureCapabilities
from .fixture import patched_fixtures
from .library import FixtureLibrary


def capabilities_of(root: etree._Element, library: FixtureLibrary) -> list[FixtureCapabilities]:
    result = []
    for fixture in patched_fixtures(root):
        definition = library.get(fixture.manufacturer, fixture.model)
        if definition is None or fixture.mode not in definition.modes:
            continue
        result.append(FixtureCapabilities.resolve(fixture, definition))
    return result
