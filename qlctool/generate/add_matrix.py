"""Build one RGBMatrix into the workspace, paced for one full pass."""

from ..argb import RGB
from ..functions.rgbmatrix import build_rgbmatrix
from ..ids import next_function_id
from ..workspace import Workspace
from .matrix_pace import matrix_pace


def add_matrix(
    workspace: Workspace,
    name: str,
    algorithm: str | None,
    mono_color: RGB,
    end_color: RGB | None,
    group_id: int,
    color_format: str,
    direction: str,
    path: str,
    properties: dict[str, str] | None,
    width: int,
    height: int,
    duration: int,
    chaser_max_hold: int,
) -> tuple[int, int]:
    """Build one RGBMatrix, add it to the workspace, and hand back what both
    call sites in `generate_matrix_effects` need next: its function id, and the
    hold one full pass of it needs. The base cross-product and a curated
    one-off recipe differ only in what they loop over and whether every result
    is stepped - this is the build-and-append shape both of them share.
    """
    frame_ms, pass_ms = matrix_pace(algorithm, width, height, duration, chaser_max_hold)
    fid = next_function_id(workspace.root)
    workspace.add_function(
        build_rgbmatrix(
            fid,
            name,
            algorithm=algorithm,
            mono_color=mono_color,
            end_color=end_color,
            group_id=group_id,
            color_format=color_format,
            duration=frame_ms,
            direction=direction,
            path=path,
            properties=properties,
        )
    )
    return fid, pass_ms
