"""What the wheel actually steps: the scene, with its extras beside it."""

from collections.abc import Sequence

from ..functions.build_collection import build_collection
from ..ids import next_function_id
from ..names.names import Names
from ..workspace import Workspace


def wheel_step(
    workspace: Workspace,
    name: str,
    scene_id: int,
    extras: Sequence[int] | None,
    path: str,
    vocabulary: Names,
) -> int:
    if not extras:
        return scene_id
    function_id = next_function_id(workspace.root)
    step_name = vocabulary.render("with_pixels", name=name)
    workspace.add_function(build_collection(function_id, step_name, [scene_id, *extras], path=path))
    return function_id
