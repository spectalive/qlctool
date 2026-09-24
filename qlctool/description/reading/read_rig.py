"""[rig]: the workspace that holds the patch, the stage plot, and where the show is written."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..rig_files import RigFiles
from .reject_unknown_keys import reject_unknown_keys


def read_rig(table: Mapping[str, Any], path: Path) -> RigFiles:
    """Paths resolved against the description's own folder. `workspace` is required."""
    here = f"{path}: [rig]"
    reject_unknown_keys(table, ("workspace", "output", "stage_plot"), here)
    for key in ("workspace", "output", "stage_plot"):
        if key in table and (not isinstance(table[key], str) or not table[key]):
            raise ValueError(f"{here} {key} must be a file name")
    if "workspace" not in table:
        raise ValueError(f"{here} workspace is required: the QLC+ workspace that holds the patch")
    folder = path.parent
    return RigFiles(
        workspace=folder / table["workspace"],
        output=folder / table["output"] if "output" in table else None,
        stage_plot=folder / table["stage_plot"] if "stage_plot" in table else None,
    )
