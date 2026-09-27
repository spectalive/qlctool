"""Build one Scene from fixture values and add it to the workspace."""

from ..functions.scene import build_scene
from ..ids import next_function_id
from ..workspace import Workspace


def add_scene(
    workspace: Workspace, name: str, values: dict[int, list[tuple[int, int]]], path: str
) -> int:
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
