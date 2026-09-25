"""Resolve capabilities for every patched fixture in a workspace.

The convenience join generators start from: workspace + library -> one
FixtureCapabilities per fixture whose model and mode the library knows
(`resolved_definition`). Fixtures with no matching definition (e.g. Generic)
are skipped, because their channel roles cannot be resolved and a generator
must not guess at them.
"""

from lxml import etree

from .capability import FixtureCapabilities
from .fixture import patched_fixtures
from .library import FixtureLibrary
from .resolved_definition import resolved_definition


def capabilities_of(root: etree._Element, library: FixtureLibrary) -> list[FixtureCapabilities]:
    result = []
    for fixture in patched_fixtures(root):
        definition = resolved_definition(fixture, library)
        if definition is None:
            continue
        result.append(FixtureCapabilities.resolve(fixture, definition))
    return result
