"""Re-lay a fixture group's heads into a grid with no holes in it.

An RGBMatrix paints the cells a group *declares*. A cell with no head in it is
a frame of every sweep where that part of the group is dark for no reason, and
a head outside the declared grid is a fixture no effect can ever reach. Both
were in this rig at once: `BarrasLed` had four empty cells where the beams used
to be, so the panels beside them sat dark for the first half of every Fill, and
`Cabezas` declared 8x1 over twelve heads, four of which no matrix could touch.

Heads keep their reading order - left to right, top to bottom, as the group
already had them - so a re-shaped group sweeps in the order it swept before.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local, iter_local


def reshape_group(root: etree._Element, group_id: int, width: int, height: int) -> None:
    """Re-place every head into a width x height grid, in reading order.

    Refuses a grid that is not exactly the size of the group, because both ways
    of being wrong are the bug this exists to remove: too small orphans heads,
    too large leaves holes.
    """
    group = _group(root, group_id)
    heads = findall_local(group, "Head")
    if width * height != len(heads):
        raise ValueError(
            f"group {group_id} ({_name(group)!r}) has {len(heads)} head(s) and "
            f"{width}x{height} is {width * height} cells: a grid that does not "
            "match leaves holes or orphans heads"
        )

    ordered = sorted(heads, key=lambda head: (int(head.attrib["Y"]), int(head.attrib["X"])))
    for index, head in enumerate(ordered):
        head.set("X", str(index % width))
        head.set("Y", str(index // width))

    size = find_local(group, "Size")
    if size is None:
        raise ValueError(f"group {group_id} has no <Size>")
    size.set("X", str(width))
    size.set("Y", str(height))


def _group(root: etree._Element, group_id: int) -> etree._Element:
    for element in iter_local(root, "FixtureGroup"):
        if element.attrib.get("ID") == str(group_id):
            return element
    raise KeyError(f"no fixture group with ID {group_id}")


def _name(group: etree._Element) -> str:
    name = find_local(group, "Name")
    return (name.text or "").strip() if name is not None else ""
