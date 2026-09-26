"""The `newshow` tool: a fresh show on an existing patch, written where the caller says."""

from typing import Any

from ..description.described_files import described_files
from ..description.description_names import description_names
from ..description.load_show_description import load_show_description
from ..generate.canonical_show import build_canonical_show
from ..library_for import library_for
from ..newshow_refusal import newshow_refusal
from ..validate import validate_workspace
from ..vibra.vibra_description import vibra_description
from ..workspace import Workspace
from .existing_path import existing_path
from .output_path import output_path
from .unresolved_models import unresolved_models


def tool_newshow(
    out: str,
    workspace: str | None = None,
    description: str | None = None,
    overwrite: bool = False,
    buttons: bool = True,
    validate: bool = False,
    fixtures: list[str] | None = None,
) -> dict[str, Any]:
    """Build the show `qlctool newshow` builds and write it to `out`.

    The patch is `workspace`, or the description's `[rig] workspace`. `out`
    is never replaced unless `overwrite` is true, so the patch cannot be lost
    by accident.
    """
    if workspace is None and description is None:
        raise ValueError("newshow needs a workspace or a description")
    described = existing_path(description) if description is not None else None
    patch = existing_path(workspace) if workspace is not None else None
    if described is not None:
        source, _ = described_files(str(patch) if patch else None, described, out)
        patch = existing_path(str(source))
    assert patch is not None
    target = output_path(out, overwrite)
    loaded = Workspace.load(patch)
    show_description = load_show_description(described, loaded.root) if described else None
    shown = show_description or vibra_description()
    library = library_for(
        fixtures, patch, show_description.rig.fixtures if show_description else ()
    )
    refusal = newshow_refusal(loaded.root, library, description_names(shown))
    if refusal is not None:
        raise ValueError(refusal)
    plot = None
    if show_description is not None and show_description.rig.stage_plot is not None:
        plot = str(show_description.rig.stage_plot)
    show = build_canonical_show(
        loaded, library, with_layout=buttons, plot_path=plot, description=show_description
    )
    loaded.save(target)
    result: dict[str, Any] = {
        "workspace": str(patch),
        "out": str(target),
        "functions": show.function_count,
        "buttons": len(show.button_ids),
        "stage_placed": show.stage_placed,
        "unresolved": unresolved_models(loaded.root, library),
    }
    if validate:
        verdict = validate_workspace(target)
        result["validation"] = {"ok": verdict.ok, "errors": list(verdict.errors)}
    return result
