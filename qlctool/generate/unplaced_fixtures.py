"""Patched fixtures the Monitor has no position for.

QLC+ draws these at the origin, on top of each other.
"""

from ..find_local import find_local
from ..findall_local import findall_local
from ..patched_fixtures import patched_fixtures
from ..workspace import Workspace


def unplaced_fixtures(workspace: Workspace) -> list[int]:
    monitor = find_local(workspace.engine, "Monitor")
    placed = (
        {int(item.attrib["ID"]) for item in findall_local(monitor, "FxItem")}
        if monitor is not None
        else set()
    )
    return [f.fixture_id for f in patched_fixtures(workspace.root) if f.fixture_id not in placed]
