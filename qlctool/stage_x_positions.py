"""Where each fixture stands across the stage, in millimetres.

The `<Monitor>` node the plot writes is the only place a workspace records the
room. `monitor_positions.house_right_fixture_ids` reads it for symmetry - which
side a fixture is on; this reads the raw coordinate, which is what ordering a
fixture group's cells needs.

Hidden fixtures are left out. A hidden item is one the plot marks as not rigged,
and a spare in a flight case should not decide where a sweep starts.
"""

from lxml import etree

from .xmlutil import find_local, iter_local


def stage_x_positions(root: etree._Element) -> dict[int, float]:
    """Fixture ID -> its X on the stage, empty when nothing has been placed."""
    engine = find_local(root, "Engine")
    monitor = find_local(engine, "Monitor") if engine is not None else None
    if monitor is None:
        return {}
    return {
        int(item.get("ID")): float(item.get("XPos", "0"))
        for item in iter_local(monitor, "FxItem")
        if item.get("ID") is not None and item.get("Hidden") is None
    }
