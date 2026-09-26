"""A chaser the canonical show adds, one hold per step."""

from ..functions.chaser import build_chaser
from ..ids import next_function_id
from ..workspace import Workspace


def show_chaser(
    workspace: Workspace,
    name: str,
    steps: list[int],
    holds: list[int],
    path: str,
) -> int:
    """A chaser of `steps` with one hold each, filed under `path`; its id."""
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_chaser(function_id, name, steps, hold=holds, path=path))
    return function_id
