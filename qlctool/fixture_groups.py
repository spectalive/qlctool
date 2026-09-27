"""All fixture groups defined in a workspace."""

from lxml import etree

from .find_local import find_local
from .findall_local import findall_local
from .fixture_group import DefinedFixtureGroup
from .iter_local import iter_local


def fixture_groups(root: etree._Element) -> list[DefinedFixtureGroup]:
    """All fixture groups defined in a workspace, in document order."""
    result = []
    for element in iter_local(root, "FixtureGroup"):
        if "ID" not in element.attrib:
            # A <FixtureGroup>0</FixtureGroup> reference inside an RGBMatrix.
            continue
        size = find_local(element, "Size")
        name = find_local(element, "Name")
        heads = findall_local(element, "Head")
        ordered: list[int] = []
        for head in heads:
            fixture_id = int(head.attrib["Fixture"])
            if fixture_id not in ordered:
                ordered.append(fixture_id)
        result.append(
            DefinedFixtureGroup(
                group_id=int(element.attrib["ID"]),
                name=(name.text or "").strip() if name is not None else "",
                width=int(size.attrib.get("X", "0")) if size is not None else 0,
                height=int(size.attrib.get("Y", "0")) if size is not None else 0,
                head_count=len(heads),
                fixture_ids=tuple(ordered),
            )
        )
    return result
