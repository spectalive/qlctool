"""The patched fixtures that hang in the room: every one the stage plot does not hide.

The plot marks a spare in a flight case with a Monitor `FxItem Hidden`
(`stage_plot.rigged`), and `house_right_fixture_ids` and `stage_x_positions`
already leave those out. A workspace with no Monitor, or a fixture the Monitor
does not list, counts as rigged: nothing says otherwise.
"""

from lxml import etree

from .find_local import find_local
from .fixture import patched_fixtures
from .iter_local import iter_local


def rigged_fixture_ids(root: etree._Element) -> set[int]:
    engine = find_local(root, "Engine")
    monitor = find_local(engine, "Monitor") if engine is not None else None
    hidden = (
        {
            int(identifier)
            for item in iter_local(monitor, "FxItem")
            if item.get("Hidden") is not None and (identifier := item.get("ID")) is not None
        }
        if monitor is not None
        else set()
    )
    return {fixture.fixture_id for fixture in patched_fixtures(root)} - hidden
