"""Find every node that references a fixture by ID.

A fixture is pointed at from six places in a workspace, in three shapes: a
`<FixtureVal ID>` in each scene, a `<Fixture><ID>` block in each EFX, a
`<Fixture ID>` in a Virtual Console XY pad, and a `Fixture=` attribute on
fixture-group heads and VC slider channels. Removing a fixture without clearing
all of them leaves QLC+ pointing at nothing, so they are enumerated in one place.
"""

from lxml import etree

from .xmlutil import find_local, localname

# Elements whose Fixture="n" attribute is a reference.
_ATTRIBUTE_REFERENCES = {"Head", "Channel"}
# Elements whose ID="n" attribute is a reference.
_ID_ATTRIBUTE_REFERENCES = {"FixtureVal"}


def fixture_references(root: etree._Element, fixture_id: int) -> list[etree._Element]:
    """Every node referencing this fixture, excluding its own patch entry."""
    wanted = str(fixture_id)
    found = []
    for element in root.iter():
        name = localname(element)
        if name in _ATTRIBUTE_REFERENCES:
            if element.attrib.get("Fixture") == wanted:
                found.append(element)
        elif name in _ID_ATTRIBUTE_REFERENCES:
            if element.attrib.get("ID") == wanted:
                found.append(element)
        elif name == "Fixture":
            if element.attrib.get("ID") == wanted:
                found.append(element)  # Virtual Console XY pad
            elif find_local(element, "Channels") is None:
                # EFX member block: <Fixture><ID>n</ID>...
                id_element = find_local(element, "ID")
                if id_element is not None and (id_element.text or "").strip() == wanted:
                    found.append(element)
    return found
