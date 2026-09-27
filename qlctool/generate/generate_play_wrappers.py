"""Collections that isolate JUGAR picks from automatic state starts.

Each wraps one original function; a pick with `companions` also starts those
beside it - the washes held while a beam-only look is picked (`wash_hold`).
"""

from collections.abc import Mapping, Sequence

from ..findall_local import findall_local
from ..names.default_names import default_names
from ..names.names import Names
from ..workspace import Workspace
from .generated_play_wrappers import GeneratedPlayWrappers as _GeneratedPlayWrappers
from .play_wrap import play_wrap
from .spaced import spaced


def generate_play_wrappers(
    workspace: Workspace,
    color_ids: Sequence[int],
    rainbow_ids: Sequence[int],
    panel_effect_ids: Sequence[int],
    panel_manual_id: int | None,
    movement_ids: Sequence[int],
    gobo_ids: Sequence[int],
    prism_ids: Sequence[int],
    names: Names | None = None,
    companions: Mapping[int, Sequence[int]] | None = None,
) -> _GeneratedPlayWrappers:
    """Wrap every play pick once, preserving each original function as its leaf."""
    vocabulary = default_names() if names is None else names

    def family(identifier: str) -> str:
        return vocabulary.render("path_play", family=vocabulary.display(identifier))

    functions = {
        int(function.attrib["ID"]): function
        for function in findall_local(workspace.engine, "Function")
        if "ID" in function.attrib
    }
    panels = spaced(panel_effect_ids, 12)
    if panel_manual_id is not None:
        panels.append(panel_manual_id)
    prefix = vocabulary.display("pick_prefix")
    gobos = vocabulary.render("path_play", family="Gobos")
    return _GeneratedPlayWrappers(
        color_ids=play_wrap(workspace, functions, color_ids, prefix, family("path_family_colour")),
        rainbow_ids=play_wrap(
            workspace, functions, rainbow_ids, prefix, family("path_family_colour")
        ),
        panel_ids=play_wrap(workspace, functions, panels, prefix, family("path_family_pixels")),
        movement_ids=play_wrap(
            workspace, functions, movement_ids, prefix, family("path_family_heads"), companions
        ),
        gobo_ids=play_wrap(workspace, functions, gobo_ids, prefix, gobos),
        prism_ids=play_wrap(workspace, functions, prism_ids, prefix, family("path_prism")),
    )
