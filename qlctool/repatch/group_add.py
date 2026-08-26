"""Create a fixture group, because a group is a kind of light, not a container.

Two things share a group only if they should share a picture. An RGBMatrix
paints one grid across every head in the group, so putting four wall panels in
the same grid as two eight-segment bars does not "include" the panels - it makes
them four cells of the bars' picture, dark for whichever part of every sweep
their columns are not in. The owner said it plainly: "los 4 pixel led no tienen
que ir con las 2 barras led, son luces diferentes" (2026-08-26).

The group starts empty and off the console's radar - no colour bank and no
matrix is generated for it until it has heads.
"""

from lxml import etree

from ..constants import QLC_NS
from ..xmlutil import find_local, iter_local


def add_fixture_group(
    root: etree._Element, name: str, width: int, height: int
) -> int:
    """Append an empty fixture group; returns the ID it was given."""
    if width < 1 or height < 1:
        raise ValueError(f"a {width}x{height} grid holds nothing")
    if not name.strip():
        raise ValueError("a fixture group needs a name: it names its own bank")

    engine = find_local(root, "Engine")
    if engine is None:
        raise ValueError("workspace has no <Engine>")

    existing = [
        element for element in iter_local(root, "FixtureGroup")
        if "ID" in element.attrib
    ]
    for element in existing:
        if _name(element) == name.strip():
            raise ValueError(f"a fixture group named {name!r} already exists")
    group_id = max((int(e.attrib["ID"]) for e in existing), default=-1) + 1

    group = etree.Element(f"{{{QLC_NS}}}FixtureGroup")
    group.set("ID", str(group_id))
    etree.SubElement(group, f"{{{QLC_NS}}}Name").text = name.strip()
    size = etree.SubElement(group, f"{{{QLC_NS}}}Size")
    size.set("X", str(width))
    size.set("Y", str(height))

    if existing:
        last = existing[-1]
        last.getparent().insert(last.getparent().index(last) + 1, group)
    else:
        engine.append(group)
    return group_id


def _name(group: etree._Element) -> str:
    name = find_local(group, "Name")
    return (name.text or "").strip() if name is not None else ""
