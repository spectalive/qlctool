"""All patched fixtures in a workspace, in document order."""

from lxml import etree

from .find_local import find_local
from .fixture import PatchedFixture
from .iter_local import iter_local


def patched_fixtures(root: etree._Element) -> list[PatchedFixture]:
    """All patched fixtures in a workspace, in document order.

    Filters to <Fixture> nodes that carry a <Channels> child, so the fixture-ID
    references QLC+ writes inside scenes and groups are not mistaken for patched
    fixtures.
    """
    result = []
    for element in iter_local(root, "Fixture"):
        if find_local(element, "Channels") is None:
            continue
        result.append(PatchedFixture.from_element(element))
    return result
