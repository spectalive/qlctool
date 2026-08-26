"""Resize a fixture group's grid.

An RGBMatrix paints the cells the group *declares*, not the heads it holds, so a
group whose `<Size>` is smaller than its own contents has heads that no effect
can ever reach. That is exactly what "BarrasLed" was: 8x2 declared over three
rows of heads, which left row 2 - the beams and the pixel panels - dark through
every matrix in the show.

The beams are no longer in that group (2026-08-26). Putting them there to fill
the grid also put them in the group's colour bank, so the bars' mix wheel and
the heads' mix wheel both drove their colour wheel - and a matrix does nothing
on a fixture with no RGB anyway. Their cells are simply empty now: see
`group_head_remove`.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local, iter_local


def set_group_size(root: etree._Element, group_id: int, width: int, height: int) -> None:
    """Set a group's grid, refusing a size that would orphan heads it holds."""
    group = _group(root, group_id)
    orphaned = [
        (int(head.attrib["X"]), int(head.attrib["Y"]))
        for head in findall_local(group, "Head")
        if int(head.attrib["X"]) >= width or int(head.attrib["Y"]) >= height
    ]
    if orphaned:
        raise ValueError(
            f"group {group_id} at {width}x{height} would leave "
            f"{len(orphaned)} head(s) outside the grid, unreachable by any "
            f"matrix: {sorted(orphaned)}"
        )
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
