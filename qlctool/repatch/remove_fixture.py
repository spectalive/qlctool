"""Unpatch a fixture and clear every reference to it.

QLC+ points at a fixture from scenes, EFX blocks, fixture-group heads, XY pads
and slider channels. Dropping the patch entry alone would leave those pointing
at nothing, so they all go. Scenes keep working - they simply stop driving the
fixture that is no longer there.
"""

from lxml import etree

from ..fixture_references import fixture_references
from .patch_element import patch_element


def remove_fixture(root: etree._Element, fixture_id: int) -> int:
    """Remove the fixture and all its references; returns the reference count."""
    element = patch_element(root, fixture_id)
    references = fixture_references(root, fixture_id)
    for reference in references:
        reference.getparent().remove(reference)
    element.getparent().remove(element)
    return len(references)
