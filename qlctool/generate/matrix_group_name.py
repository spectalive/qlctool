"""The name an RGBMatrix's fixture group goes by in the show."""

from ..constants import ALL_FIXTURES_GROUP
from ..fixture_group import fixture_groups
from ..names.names import Names
from ..workspace import Workspace


def matrix_group_name(workspace: Workspace, group_id: int, vocabulary: Names) -> str:
    if group_id == ALL_FIXTURES_GROUP:
        return vocabulary.display("all_fixtures_group")
    for group in fixture_groups(workspace.root):
        if group.group_id == group_id:
            return group.name
    known = ", ".join(f"{g.group_id}={g.name}" for g in fixture_groups(workspace.root))
    raise ValueError(f"workspace defines no fixture group {group_id} (have: {known or 'none'})")
