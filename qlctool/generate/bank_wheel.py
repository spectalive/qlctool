"""The Random-order chaser that cycles one bank's scenes when nobody is at the console."""

from ..functions.chaser import build_chaser
from ..ids import next_function_id
from ..workspace import Workspace


def bank_wheel(
    workspace: Workspace,
    name: str,
    scene_ids: list[int],
    hold: int,
    fade: int,
    path: str,
) -> int | None:
    """A Random-order chaser: unattended, a fixed order reads as a loop."""
    if not scene_ids:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            function_id,
            name,
            scene_ids,
            fade_in=fade,
            hold=hold,
            fade_out=fade,
            run_order="Random",
            path=path,
        )
    )
    return function_id
