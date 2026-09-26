"""The patched models a tool could not read, said as data instead of a stderr line."""

from lxml import etree

from ..library import FixtureLibrary
from ..unresolved_fixtures import unresolved_fixtures


def unresolved_models(root: etree._Element, library: FixtureLibrary) -> list[str]:
    """`Manufacturer Model <mode>` for every model and mode with no usable definition."""
    return [
        f"{fixture.manufacturer} {fixture.model} <{fixture.mode}>"
        for fixture in unresolved_fixtures(root, library)
    ]
