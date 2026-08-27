"""Rotate the dimmer programmes with a steady full-intensity breath.

The hand-built show did not run its three intensity movements back to back:
each one returned to a stable full look first. That pause keeps a whole minute
of moving dimmers from reading as a fault or a permanently restless room, and
it gives every programme the same visible starting point.
"""

from collections.abc import Sequence

from ..functions.chaser import build_chaser
from ..ids import next_function_id
from ..workspace import Workspace


def generate_dimmer_sequence(
    workspace: Workspace,
    breath_id: int,
    program_ids: Sequence[int],
    breath_hold: int = 20000,
    program_hold: int = 10000,
    path: str = "Dimmers",
) -> int:
    """Build the looping breath/program rotation and return its function ID."""
    if not program_ids:
        raise ValueError("the dimmer sequence needs at least one programme")

    steps: list[int] = []
    holds: list[int] = []
    for program_id in program_ids:
        steps.extend((breath_id, program_id))
        holds.extend((breath_hold, program_hold))

    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            function_id,
            "Dimmer Secuencia",
            steps,
            hold=holds,
            run_order="Loop",
            path=path,
        )
    )
    return function_id
