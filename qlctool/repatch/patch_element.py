"""Find a patched fixture's own <Fixture> node in the Engine.

Every re-patch operation edits that node, and it must not be confused with the
fixture *references* of the same tag name inside EFX functions and the Virtual
Console - the patch entry is the one carrying <Channels>.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local


def patch_element(root: etree._Element, fixture_id: int) -> etree._Element:
    engine = find_local(root, "Engine")
    if engine is not None:
        for element in findall_local(engine, "Fixture"):
            id_element = find_local(element, "ID")
            if id_element is None or find_local(element, "Channels") is None:
                continue
            if (id_element.text or "").strip() == str(fixture_id):
                return element
    raise KeyError(f"no patched fixture with ID {fixture_id}")
