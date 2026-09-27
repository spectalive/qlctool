"""Which fixtures stand on the house-right half of the stage.

Read back out of the `<Monitor>` node the plot writes, because the one thing a
rig needs positions for beyond drawing itself is symmetry: a movement effect
that runs the same way on both sides sweeps the whole rig in parallel, where the
pair opening and closing together is what reads as designed. Reversing the EFX
direction on one side is how that is done, and this says which side a fixture is
on.

The comparison is against the middle of the stage grid, in millimetres - the
grid is stored in metres and the positions in millimetres, as everywhere else in
QLC+ - and a fixture exactly on the centre line counts as house left, so a
single centre fixture is not left alone in its own half.
"""

from lxml import etree

from .xmlutil import find_local, iter_local


def house_right_fixture_ids(root: etree._Element) -> set[int]:
    """Fixture IDs positioned past the centre of the stage, hidden ones aside.

    Empty when the workspace has no Monitor node or no stage width: no
    positions means no sides, and mirroring a rig that has not been placed
    would be guesswork.
    """
    monitor = find_local(find_local(root, "Engine"), "Monitor")
    if monitor is None:
        return set()

    grid = find_local(monitor, "Grid")
    if grid is None:
        return set()
    width_mm = float(grid.get("Width", "0")) * 1000
    if width_mm <= 0:
        return set()

    centre = width_mm / 2
    return {
        int(item.get("ID"))
        for item in iter_local(monitor, "FxItem")
        if item.get("Hidden") is None
        and item.get("ID") is not None
        and float(item.get("XPos", "0")) > centre
    }
