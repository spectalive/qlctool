"""The grid of the fixture group an RGBMatrix paints."""

from ..fixture_group import fixture_groups
from ..workspace import Workspace


def matrix_grid(workspace: Workspace, group_id: int) -> tuple[int, int]:
    """The grid a matrix paints, which is what decides how long a pass takes."""
    for group in fixture_groups(workspace.root):
        if group.group_id == group_id:
            return group.width, group.height
    return 1, 1
