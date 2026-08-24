"""Build a fresh show from a rig: patch in, generated content out.

The two DeluxeEventos workspaces grew by hand over years and nobody knows what
half of their 377 functions do. The plan agreed with the owner is to keep the
patch, drop the content and regenerate it: a colour palette, matrix effects per
fixture group, movement across the heads, and a Virtual Console laid out for all
of it. Everything here is reproducible from this one call, which is the whole
point - a show you can rebuild is a show you can change.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from ..fixture_group import fixture_groups
from ..library import FixtureLibrary
from ..palette import PALETTE
from ..skeleton import strip_to_skeleton
from ..workspace import Workspace
from .color_palette import generate_color_palette
from .matrix_effects import generate_matrix_effects
from .movement_efx import generate_movement_efx
from .vc_layout import generate_vc_layout

# Enough shapes to play a set with, without burying the console in buttons.
SHOW_ALGORITHMS: tuple[str | None, ...] = (
    "Fill", "Even/Odd", "Strobe", "Waves", None,
)
SHOW_COLORS = ("Rojo", "Verde", "Azul", "Ambar", "Magenta", "Blanco")


@dataclass(frozen=True)
class CanonicalShow:
    scene_ids: list[int]
    matrix_ids: list[int]
    efx_ids: list[int]
    chaser_ids: list[int]
    button_ids: list[int]

    @property
    def function_count(self) -> int:
        return (
            len(self.scene_ids) + len(self.matrix_ids)
            + len(self.efx_ids) + len(self.chaser_ids)
        )


def build_canonical_show(
    workspace: Workspace,
    library: FixtureLibrary,
    algorithms: Sequence[str | None] = SHOW_ALGORITHMS,
    colors: Sequence[str] = SHOW_COLORS,
    with_layout: bool = True,
) -> CanonicalShow:
    """Strip the workspace to its patch and generate a whole show onto it."""
    strip_to_skeleton(workspace)
    subset = {name: PALETTE[name] for name in colors}

    palette = generate_color_palette(workspace, library, palette=subset)
    chaser_ids = [] if palette.chaser_id is None else [palette.chaser_id]

    matrix_ids: list[int] = []
    for group in fixture_groups(workspace.root):
        matrices = generate_matrix_effects(
            workspace,
            group_id=group.group_id,
            algorithms=algorithms,
            palette=subset,
            path=f"Matrices {group.name} (generado)",
        )
        matrix_ids.extend(matrices.matrix_ids)
        if matrices.chaser_id is not None:
            chaser_ids.append(matrices.chaser_id)

    movement = generate_movement_efx(workspace, library)
    if movement.chaser_id is not None:
        chaser_ids.append(movement.chaser_id)

    button_ids: list[int] = []
    if with_layout:
        button_ids = generate_vc_layout(workspace).button_ids

    return CanonicalShow(
        scene_ids=palette.scene_ids,
        matrix_ids=matrix_ids,
        efx_ids=movement.efx_ids,
        chaser_ids=chaser_ids,
        button_ids=button_ids,
    )
