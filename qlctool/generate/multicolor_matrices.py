"""The pixel groups' part of the multicolour look: one Plasma per group.

A multicolour scene cannot paint a bar - the bars belong to their matrix, and
a scene writing their RGB beside it is the two-sources bug. So the wild wheel
steps start these instead: plasma.js on its Rainbow preset, the whole gradient
sliding across the group, which on a multicolour step is exactly the job. Same
contract as `pixel_wheel_matrices`: paced so a pass fits inside a wheel step.
"""

from collections.abc import Sequence

from ..color_format import color_format_of
from ..fixture_group import fixture_groups
from ..functions.rgbmatrix import build_rgbmatrix
from ..ids import next_function_id
from ..matrix_step_count import matrix_step_count
from ..workspace import Workspace

ALGORITHM = "Plasma"
FRAME_MS = 478


def generate_multicolor_matrices(
    workspace: Workspace,
    group_ids: Sequence[int],
    fit_ms: int = 2500,
    path: str = "Colores Rig",
) -> list[int]:
    """One rainbow Plasma matrix per pixel group, paced to the wheel's hold."""
    color_format = color_format_of(workspace.root)
    matrix_ids: list[int] = []
    for group in fixture_groups(workspace.root):
        if group.group_id not in set(group_ids):
            continue
        count = matrix_step_count(ALGORITHM, group.width, group.height)
        frame_ms = min(FRAME_MS, max(1, fit_ms // count))
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_rgbmatrix(
                function_id,
                f"{group.name} - Plasma Rainbow (Rueda)",
                algorithm=ALGORITHM,
                mono_color=(255, 255, 255),
                group_id=group.group_id,
                color_format=color_format,
                duration=frame_ms,
                properties={"presetIndex": "Rainbow"},
                path=path,
            )
        )
        matrix_ids.append(function_id)
    return matrix_ids
