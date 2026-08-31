"""Re-lay a fixture group's cells in the order the fixtures stand in the room.

A matrix paints the grid a group declares, and half of QLC+'s scripts mean a
direction. A group built in patch order is in DMX address order, which is
cabling order, which is nobody's idea of left to right: `Cabezas` walked its
four rigged beams 1916, 9694, 4405, 7205 mm across the stage, so every sweep
over the moving heads went left, far right, back to the middle.

Sorting is by the `<Monitor>` X the plot writes, and ties break on the cell the
head already had. That second half is what keeps everything the stage cannot
speak about exactly as it was: an LED bar's eight segments share one position
and their order is the bar's, two fixtures rigged at the same spot keep the
order somebody chose, and the fixtures the plot has not placed - which all tie
with each other - go last in the order they were already in. A spare in a flight
case cannot be anywhere in a sweep, and putting it in the middle would leave a
hole in the run of the ones that are really there.

Rows are preserved. A head stays on its own Y and is only re-lettered across
that row, because moving it to another row would change which slice of a
two-row pattern it belongs to - a different question, and one for the rig.
"""

from lxml import etree

from ..stage_x_positions import stage_x_positions
from ..xmlutil import findall_local, iter_local


def sort_group_by_stage(root: etree._Element, group_id: int) -> list[tuple[int, int]]:
    """Re-lay every row of the group in stage order; returns the cells moved.

    Each entry is the (from x, to x) of a head that changed cell. An empty list
    means the group was already in order.
    """
    positions = stage_x_positions(root)
    if not positions:
        raise ValueError(
            "this workspace has no fixture positions, so it has no stage order; "
            "run `qlctool stage --plot ...` first"
        )

    group = _group(root, group_id)
    rows: dict[int, list[etree._Element]] = {}
    for head in findall_local(group, "Head"):
        rows.setdefault(int(head.attrib["Y"]), []).append(head)

    moved: list[tuple[int, int]] = []
    for heads in rows.values():
        cells = sorted(int(head.attrib["X"]) for head in heads)
        ordered = sorted(
            heads,
            key=lambda head: (
                positions.get(int(head.attrib["Fixture"])) is None,
                positions.get(int(head.attrib["Fixture"]), 0.0),
                int(head.attrib["X"]),
            ),
        )
        for cell, head in zip(cells, ordered):
            was = int(head.attrib["X"])
            if was != cell:
                moved.append((was, cell))
            head.set("X", str(cell))
    return moved


def _group(root: etree._Element, group_id: int) -> etree._Element:
    for element in iter_local(root, "FixtureGroup"):
        if element.attrib.get("ID") == str(group_id):
            return element
    raise KeyError(f"no fixture group with ID {group_id}")
