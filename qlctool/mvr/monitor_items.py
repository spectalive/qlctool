"""Read the `<Monitor>` node back: the stage and where every fixture sits.

The inverse of `write_monitor`, for exports that need the rig's layout rather
than the workspace's. Positions come back as QLC+ stores them - the near
corner, in millimetres - and the stage in millimetres too, so a caller works
in one unit.
"""

from lxml import etree

from ..monitor_node import MonitorItem
from ..xmlutil import find_local, iter_local
from .monitor_stage import MonitorStage

MM_PER_M = 1000.0


def monitor_items(root: etree._Element) -> MonitorStage | None:
    """None when the workspace has no Monitor node: nothing has been placed."""
    engine = find_local(root, "Engine")
    monitor = find_local(engine, "Monitor") if engine is not None else None
    if monitor is None:
        return None
    grid = find_local(monitor, "Grid")
    stage = tuple(
        float(grid.get(axis, "0") if grid is not None else "0") * MM_PER_M
        for axis in ("Width", "Height", "Depth")
    )
    items = [
        MonitorItem(
            fixture_id=int(item.get("ID")),
            x=float(item.get("XPos", "0")),
            y=float(item.get("YPos", "0")),
            z=float(item.get("ZPos", "0")),
            hidden=item.get("Hidden") is not None,
            x_rot=float(item.get("XRot", "0")),
            y_rot=float(item.get("YRot", "0")),
            z_rot=float(item.get("ZRot", "0")),
        )
        for item in iter_local(monitor, "FxItem")
        if item.get("ID") is not None
    ]
    return MonitorStage(stage=(stage[0], stage[1], stage[2]), items=items)
