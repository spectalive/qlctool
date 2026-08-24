"""Rename a patched fixture.

Only the <Name> the console shows; the fixture ID everything references is
untouched, so no function, group or Virtual Console widget needs updating.
"""

from lxml import etree

from ..xmlutil import find_local
from .patch_element import patch_element


def rename_fixture(root: etree._Element, fixture_id: int, name: str) -> str:
    """Set the fixture's display name; returns the previous one."""
    element = patch_element(root, fixture_id)
    name_element = find_local(element, "Name")
    previous = (name_element.text or "").strip()
    name_element.text = name
    return previous
