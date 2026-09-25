"""Generate a grid of RGBMatrix effects: every algorithm in every colour.

The show leans on RGBMatrix more than anything else (122 of them), and they are
all the same shape: one fixture group, one script algorithm, one colour. Building
that matrix of combinations by hand is the single biggest time sink in QLC+, so
this does the whole cross-product in one call, optionally chained into a chaser.
"""

from collections.abc import Mapping, Sequence

from ..argb import RGB
from ..color_format import color_format_of
from ..constants import ALL_FIXTURES_GROUP
from ..functions.chaser import build_chaser
from ..ids import next_function_id
from ..matrix_algorithms import SCRIPT_ALGORITHMS, CuratedScript
from ..names.default_names import default_names
from ..names.names import Names
from ..palette import PALETTE
from ..workspace import Workspace
from .add_matrix import add_matrix
from .generated_matrices import GeneratedMatrices
from .matrix_grid import matrix_grid
from .matrix_group_name import matrix_group_name


def generate_matrix_effects(
    workspace: Workspace,
    group_id: int = ALL_FIXTURES_GROUP,
    algorithms: Sequence[str | None] = SCRIPT_ALGORITHMS,
    palette: dict[str, RGB] | None = None,
    path: str | None = None,
    make_chaser: bool = True,
    duration: int = 478,
    direction: str = "Forward",
    chaser_hold: int = 2000,
    chaser_max_hold: int = 8000,
    chaser_algorithms: Sequence[str | None] | None = None,
    curated: Sequence[CuratedScript] = (),
    curated_palette: Mapping[str, RGB] | None = None,
    names: Names | None = None,
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

    `curated` is a different shape: one hand-tuned matrix per entry, with its
    own properties and its own one or two colours (`matrix_algorithms.
    CuratedScript`), rather than a cross-product over `colors`. Every entry is
    always stepped into the chaser - there is no separate restriction for
    these, they were chosen one at a time already.

    `names` is the show's vocabulary: the cycle's name, the whole-rig group's
    name and the default `path` come from it.
    """
    vocabulary = default_names() if names is None else names
    path = vocabulary.display("path_matrices_generated") if path is None else path
    colors = palette if palette is not None else PALETTE
    group_name = matrix_group_name(workspace, group_id, vocabulary)
    # Write the colour shape this show already uses (4.13 vs 4.14+).
    color_format = color_format_of(workspace.root)

    width, height = matrix_grid(workspace, group_id)
    stepped = algorithms if chaser_algorithms is None else chaser_algorithms

    matrix_ids: list[int] = []
    steps: list[tuple[int, int]] = []  # (function id, hold for one full pass)
    for algorithm in algorithms:
        label = "Solid" if algorithm is None else algorithm
        for color_name, rgb in colors.items():
            fid, pass_ms = add_matrix(
                workspace,
                f"{group_name} - {label} {color_name}",
                algorithm,
                rgb,
                None,
                group_id,
                color_format,
                direction,
                path,
                None,
                width,
                height,
                duration,
                chaser_max_hold,
            )
            matrix_ids.append(fid)
            if algorithm in stepped:
                steps.append((fid, max(chaser_hold, pass_ms)))

    curated_colors = PALETTE if curated_palette is None else curated_palette
    for entry in curated:
        fid, pass_ms = add_matrix(
            workspace,
            f"{group_name} - {entry.algorithm} {'/'.join(entry.colors)}",
            entry.algorithm,
            curated_colors[entry.colors[0]],
            curated_colors[entry.colors[1]] if len(entry.colors) > 1 else None,
            group_id,
            color_format,
            direction,
            path,
            entry.properties,
            width,
            height,
            duration,
            chaser_max_hold,
        )
        matrix_ids.append(fid)
        steps.append((fid, max(chaser_hold, pass_ms)))

    chaser_id: int | None = None
    if make_chaser and steps:
        chaser_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                chaser_id,
                vocabulary.render("cycle", what=vocabulary.render("matrices_of", group=group_name)),
                [fid for fid, _ in steps],
                hold=[hold for _, hold in steps],
                # Random like the old 121-step bar cycle (and every other
                # cycle in this show): unattended, a fixed order reads as a
                # loop. Restored 2026-08-28 with the old algorithm families.
                run_order="Random",
                path=path,
            )
        )

    return GeneratedMatrices(matrix_ids=matrix_ids, chaser_id=chaser_id)
