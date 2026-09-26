"""A collection the canonical show adds."""

from ..functions.collection import build_collection
from ..ids import next_function_id
from ..workspace import Workspace
from .show_path import SHOW_PATH


def show_collection(workspace: Workspace, name: str, members: list[int]) -> int:
    """A collection of `members` filed under the show's folder; its id."""
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_collection(function_id, name, members, path=SHOW_PATH))
    return function_id
