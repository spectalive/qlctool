"""Put a fixture's head into a cell of a fixture group.

Group membership is not cosmetic: the colour banks and the matrices are both
generated *per group*, so a fixture outside every group gets only the handful of
rig-wide scenes. A pixel panel patched but ungrouped sits dark while the panel
next to it changes colour all night.
"""

from lxml import etree

from ..constants import QLC_NS
from ..fixture import patched_fixtures
from ..xmlutil import find_local, findall_local, iter_local


def add_group_head(
    root: etree._Element,
    group_id: int,
    fixture_id: int,
    x: int,
    y: int,
    head: int = 0,
) -> None:
    """Place one head at (x, y), refusing an occupied cell or a cell off-grid."""
    if fixture_id not in {f.fixture_id for f in patched_fixtures(root)}:
        raise ValueError(f"fixture {fixture_id} is not patched")

    group = _group(root, group_id)
    size = find_local(group, "Size")
    width, height = int(size.attrib["X"]), int(size.attrib["Y"])
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(
            f"cell ({x}, {y}) is outside group {group_id}'s {width}x{height} "
            "grid; resize it first or an effect will never reach the head"
        )

    for existing in findall_local(group, "Head"):
        if (int(existing.attrib["X"]), int(existing.attrib["Y"])) == (x, y):
            raise ValueError(
                f"cell ({x}, {y}) of group {group_id} already holds fixture "
                f"{existing.attrib['Fixture']}"
            )
        if (int(existing.attrib["Fixture"]), int(existing.text or 0)) == (fixture_id, head):
            raise ValueError(
                f"head {head} of fixture {fixture_id} is already in group "
                f"{group_id} at ({existing.attrib['X']}, "
                f"{existing.attrib['Y']}); a head in two cells is almost "
                "always a mistake"
            )

    element = etree.SubElement(group, f"{{{QLC_NS}}}Head")
    element.set("X", str(x))
    element.set("Y", str(y))
    element.set("Fixture", str(fixture_id))
    element.text = str(head)


def _group(root: etree._Element, group_id: int) -> etree._Element:
    for element in iter_local(root, "FixtureGroup"):
        if element.attrib.get("ID") == str(group_id):
            return element
    raise KeyError(f"no fixture group with ID {group_id}")
