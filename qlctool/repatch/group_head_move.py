"""Move a head that is already in a fixture group to a different cell.

`add_group_head` refuses a head it has seen before - a head in two cells is
almost always a mistake, and that refusal is right. But it left no way to say
"the same head, somewhere else": laying a group out by hand meant removing the
fixture and adding it back, which is two edits and a group that is briefly
wrong, and `remove_group_head` refuses outright when the fixture is the last one
in the group. That is why the split show's `PAR` group is a 7x3 grid with the
CLB2.4 heads bolted to the right of the PC-64 block instead of the 8x2 that
reads like the rig (owner's plot, 2026-08-25).

The grid is not decoration: a matrix paints the cells the group declares, so
where a head sits is where it appears in every pattern.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local, iter_local


def move_group_head(
    root: etree._Element,
    group_id: int,
    fixture_id: int,
    x: int,
    y: int,
    head: int = 0,
) -> tuple[int, int]:
    """Move one head to (x, y); returns the cell it came from.

    Raises when the group or the head does not exist, when the target is off
    the grid, or when another head already holds it - swapping two heads is two
    calls with a free cell in between, so that no move can silently overwrite a
    placement.
    """
    group = _group(root, group_id)
    size = find_local(group, "Size")
    width, height = int(size.attrib["X"]), int(size.attrib["Y"])
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(
            f"cell ({x}, {y}) is outside group {group_id}'s {width}x{height} "
            "grid; resize it first or an effect will never reach the head"
        )

    moving = None
    for existing in findall_local(group, "Head"):
        cell = (int(existing.attrib["X"]), int(existing.attrib["Y"]))
        if (int(existing.attrib["Fixture"]), int(existing.text or 0)) == (fixture_id, head):
            moving = existing
        elif cell == (x, y):
            raise ValueError(
                f"cell ({x}, {y}) of group {group_id} already holds fixture "
                f"{existing.attrib['Fixture']}; move that one out first"
            )

    if moving is None:
        raise ValueError(
            f"head {head} of fixture {fixture_id} is not in group {group_id}; "
            "use --group-add to put it there"
        )

    was = (int(moving.attrib["X"]), int(moving.attrib["Y"]))
    moving.set("X", str(x))
    moving.set("Y", str(y))
    return was


def _group(root: etree._Element, group_id: int) -> etree._Element:
    for element in iter_local(root, "FixtureGroup"):
        if element.attrib.get("ID") == str(group_id):
            return element
    raise KeyError(f"no fixture group with ID {group_id}")
