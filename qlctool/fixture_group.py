"""Read the <FixtureGroup> grids a workspace defines.

An RGBMatrix paints onto a fixture group's X/Y grid, so generating matrix
effects "for the LED bars" needs the group's ID and name. This reads only the
group definitions; the same local name also appears inside RGBMatrix functions
as a plain ID reference, and those are filtered out.
"""

from dataclasses import dataclass

from lxml import etree

from .xmlutil import find_local, findall_local, iter_local


@dataclass(frozen=True)
class DefinedFixtureGroup:
    group_id: int
    name: str
    width: int
    height: int
    head_count: int
    fixture_ids: tuple[int, ...]  # in grid order, each fixture once


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
