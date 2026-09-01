"""Generate a whole palette of colour scenes at once, plus a cycle chaser.

This is the headline hours-saver: one call turns a palette into one Scene per
colour across every RGB fixture, and optionally a Chaser that cycles them. All
functions get fresh unique IDs and are injected into the workspace in order.
Returns the created scene IDs and the chaser ID (or None).
"""

from dataclasses import dataclass

from ..capabilities_of import capabilities_of
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..palette import PALETTE
from ..workspace import Workspace
from .color_scene import color_scene_values


@dataclass(frozen=True)
class GeneratedPalette:
    scene_ids: list[int]
    chaser_id: int | None


def generate_color_palette(
    workspace: Workspace,
    library: FixtureLibrary,
    palette: dict[str, tuple[int, int, int]] | None = None,
    path: str = "Colores (generado)",
    make_chaser: bool = True,
    chaser_hold: int = 1000,
    chaser_fade: int = 500,
) -> GeneratedPalette:
    colors = palette if palette is not None else PALETTE
    caps = capabilities_of(workspace.root, library)

    scene_ids: list[int] = []
    for name, rgb in colors.items():
        fid = next_function_id(workspace.root)
        values = color_scene_values(caps, rgb)
        workspace.add_function(build_scene(fid, f"Color {name}", values, path=path))
        scene_ids.append(fid)

    chaser_id: int | None = None
    if make_chaser and scene_ids:
        chaser_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                chaser_id,
                "Ciclo Colores",
                scene_ids,
                fade_in=chaser_fade,
                hold=chaser_hold,
                fade_out=chaser_fade,
                path=path,
            )
        )

    return GeneratedPalette(scene_ids=scene_ids, chaser_id=chaser_id)
