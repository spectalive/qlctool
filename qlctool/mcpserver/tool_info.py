"""The `info` tool: what is patched, and what each fixture can do."""

from typing import Any

from ..capabilities_of import capabilities_of
from ..fixture_group import fixture_groups
from ..library_for import library_for
from ..workspace import Workspace
from .existing_path import existing_path
from .unresolved_models import unresolved_models


def tool_info(workspace: str, fixtures: list[str] | None = None) -> dict[str, Any]:
    """The patched fixtures with their roles and the fixture groups, as `qlctool info` lists them.

    Universe and address are 1-based, as QLC+ shows them and `live_channels` takes them.
    """
    path = existing_path(workspace)
    root = Workspace.load(path).root
    library = library_for(fixtures, path)
    return {
        "workspace": str(path),
        "fixtures": [
            {
                "id": c.fixture.fixture_id,
                "name": c.fixture.name,
                "universe": c.fixture.universe + 1,
                "address": c.fixture.address + 1,
                "manufacturer": c.fixture.manufacturer,
                "model": c.fixture.model,
                "mode": c.fixture.mode,
                "roles": sorted(c.roles),
            }
            for c in capabilities_of(root, library)
        ],
        "groups": [
            {
                "id": g.group_id,
                "name": g.name,
                "width": g.width,
                "height": g.height,
                "heads": g.head_count,
            }
            for g in fixture_groups(root)
        ],
        "unresolved": unresolved_models(root, library),
    }
