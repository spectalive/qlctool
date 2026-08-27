"""One matrix per wheel colour, for the pixel groups to ride the wheel with.

Two chasers that each rotate colour never agree - the wheel had the room on
cyan while the bars' own cycle had them on magenta ("van con los colores a su
bola", owner, 2026-08-26) - and QLC+ has no way to slave one chaser's steps to
another's. What it does have is Collections: a wheel step that starts the rig
scene *and* a matrix of the same colour changes both on the same tick. These
are those matrices: for each pixel group, one per wheel colour, the algorithm
rotating through the cycle's repertoire so the bars still move.

Each matrix is paced so one full pass fits inside a wheel step. The colour is
constant within a step, so a pass cut by a fast step would not show as the
half-lit bar the standalone cycle produced - but an animation that completes
is an animation somebody designed, and the frame time is where that is said.
"""

from collections.abc import Sequence

from ..argb import RGB
from ..color_format import color_format_of
from ..fixture_group import fixture_groups
from ..functions.rgbmatrix import build_rgbmatrix
from ..ids import next_function_id
from ..matrix_step_count import matrix_step_count
from ..workspace import Workspace

# The wheel's own pace: `generate_unison_colors` holds each colour this long,
# and a pass that takes longer than the hold is a pass the step cuts off.
WHEEL_HOLD = 2500
FRAME_MS = 478


def generate_pixel_wheel_matrices(
    workspace: Workspace,
    group_ids: Sequence[int],
    colors: dict[str, RGB],
    algorithms: Sequence[str | None],
    fit_ms: int = WHEEL_HOLD,
    path: str = "Colores Rig",
) -> dict[str, list[int]]:
    """colour name -> the matrices a wheel step of that colour also starts.

    One matrix per (pixel group, colour); the algorithm walks `algorithms` as
    the colour list advances, so consecutive wheel colours draw differently.
    """
    color_format = color_format_of(workspace.root)
    groups = [g for g in fixture_groups(workspace.root) if g.group_id in set(group_ids)]

    by_color: dict[str, list[int]] = {}
    for index, (name, rgb) in enumerate(colors.items()):
        algorithm = algorithms[index % len(algorithms)]
        label = "Solid" if algorithm is None else algorithm
        for group in groups:
            count = matrix_step_count(algorithm, group.width, group.height)
            frame_ms = min(FRAME_MS, max(1, fit_ms // count))
            function_id = next_function_id(workspace.root)
            workspace.add_function(
                build_rgbmatrix(
                    function_id,
                    f"{group.name} - {label} {name} (Rueda)",
                    algorithm=algorithm,
                    mono_color=rgb,
                    group_id=group.group_id,
                    color_format=color_format,
                    duration=frame_ms,
                    path=path,
                )
            )
            by_color.setdefault(name, []).append(function_id)
    return by_color
