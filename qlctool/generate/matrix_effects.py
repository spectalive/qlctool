"""Generate a grid of RGBMatrix effects: every algorithm in every colour.

The show leans on RGBMatrix more than anything else (122 of them), and they are
all the same shape: one fixture group, one script algorithm, one colour. Building
that matrix of combinations by hand is the single biggest time sink in QLC+, so
this does the whole cross-product in one call, optionally chained into a chaser.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from ..argb import RGB
from ..color_format import color_format_of
from ..constants import ALL_FIXTURES_GROUP
from ..fixture_group import fixture_groups
from ..functions.chaser import build_chaser
from ..functions.rgbmatrix import build_rgbmatrix
from ..ids import next_function_id
from ..matrix_algorithms import SCRIPT_ALGORITHMS
from ..matrix_step_count import matrix_step_count
from ..palette import PALETTE
from ..workspace import Workspace


@dataclass(frozen=True)
class GeneratedMatrices:
    matrix_ids: list[int]
    chaser_id: int | None


def generate_matrix_effects(
    workspace: Workspace,
    group_id: int = ALL_FIXTURES_GROUP,
    algorithms: Sequence[str | None] = SCRIPT_ALGORITHMS,
    palette: dict[str, RGB] | None = None,
    path: str = "Matrices (generado)",
    make_chaser: bool = True,
    duration: int = 478,
    direction: str = "Forward",
    chaser_hold: int = 2000,
    chaser_max_hold: int = 8000,
    chaser_algorithms: Sequence[str | None] | None = None,
) -> GeneratedMatrices:
    """Create one RGBMatrix per (algorithm, colour) for one fixture group.

    An entry of None in algorithms generates the solid-colour matrix
    (`Algorithm Type="Plain"`). group_id must be a group the workspace defines,
    or ALL_FIXTURES_GROUP - a matrix pointing at a group that does not exist
    loads but paints nothing, so it is rejected here.

    The chaser holds each matrix for **one full pass of its own animation**,
    not for a flat interval: an RGBMatrix walks a fixed number of frames that
    depends on the script and the grid, and a shorter hold cuts the animation
    off wherever it had got to. An effect too long for `chaser_max_hold` is
    sped up rather than cut short - a wave across fifteen PARs runs quicker,
    but it still gets to the end. `chaser_algorithms` restricts which of them
    the chaser steps at all; the matrices themselves are still generated, for
    the console to reach by hand.
    """
    colors = palette if palette is not None else PALETTE
    group_name = _group_name(workspace, group_id)
    # Write the colour shape this show already uses (4.13 vs 4.14+).
    color_format = color_format_of(workspace.root)

    width, height = _grid(workspace, group_id)
    stepped = algorithms if chaser_algorithms is None else chaser_algorithms

    matrix_ids: list[int] = []
    steps: list[tuple[int, int]] = []  # (function id, hold for one full pass)
    for algorithm in algorithms:
        frame_ms, pass_ms = _pace(
            algorithm, width, height, duration, chaser_max_hold
        )
        for color_name, rgb in colors.items():
            fid = next_function_id(workspace.root)
            label = "Solid" if algorithm is None else algorithm
            workspace.add_function(
                build_rgbmatrix(
                    fid,
                    f"{group_name} - {label} {color_name}",
                    algorithm=algorithm,
                    mono_color=rgb,
                    group_id=group_id,
                    color_format=color_format,
                    duration=frame_ms,
                    direction=direction,
                    path=path,
                )
            )
            matrix_ids.append(fid)
            if algorithm in stepped:
                steps.append((fid, max(chaser_hold, pass_ms)))

    chaser_id: int | None = None
    if make_chaser and steps:
        chaser_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                chaser_id,
                f"Ciclo Matrices {group_name}",
                [fid for fid, _ in steps],
                hold=[hold for _, hold in steps],
                path=path,
            )
        )

    return GeneratedMatrices(matrix_ids=matrix_ids, chaser_id=chaser_id)


def _pace(
    algorithm: str | None, width: int, height: int, duration: int, cap: int
) -> tuple[int, int]:
    """Frame length and full-pass length for one algorithm on one grid.

    A pass longer than the cap is run faster rather than cut off: a wave across
    fifteen PARs at the nominal frame rate would hold one colour for ten
    seconds, and holding it is as wrong as cutting it.
    """
    count = matrix_step_count(algorithm, width, height)
    frame_ms = duration
    if duration * count > cap:
        frame_ms = max(1, cap // count)
    return frame_ms, frame_ms * count


def _grid(workspace: Workspace, group_id: int) -> tuple[int, int]:
    """The grid a matrix paints, which is what decides how long a pass takes."""
    for group in fixture_groups(workspace.root):
        if group.group_id == group_id:
            return group.width, group.height
    return 1, 1


def _group_name(workspace: Workspace, group_id: int) -> str:
    if group_id == ALL_FIXTURES_GROUP:
        return "Todos"
    for group in fixture_groups(workspace.root):
        if group.group_id == group_id:
            return group.name
    known = ", ".join(
        f"{g.group_id}={g.name}" for g in fixture_groups(workspace.root)
    )
    raise ValueError(
        f"workspace defines no fixture group {group_id} (have: {known or 'none'})"
    )
