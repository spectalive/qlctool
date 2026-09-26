"""The `deskmap` tool: the tablet desk's map of a saved show."""

import json
from typing import Any

from ..build_deskmap import build_deskmap
from ..description.description_names import description_names
from ..description.load_show_description import load_show_description
from ..library_for import library_for
from ..workspace import Workspace
from .existing_path import existing_path
from .output_path import output_path


def tool_deskmap(
    workspace: str,
    description: str | None = None,
    out: str | None = None,
    overwrite: bool = False,
    fixtures: list[str] | None = None,
) -> dict[str, Any]:
    """The map `qlctool deskmap` writes; with `out`, written there byte for byte as the CLI does."""
    path = existing_path(workspace)
    loaded = Workspace.load(path)
    names = None
    if description is not None:
        names = description_names(load_show_description(existing_path(description), loaded.root))
    deskmap = build_deskmap(loaded, library_for(fixtures, path), path, names=names)
    if out is None:
        return deskmap
    target = output_path(out, overwrite)
    target.write_text(json.dumps(deskmap, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "out": str(target),
        "controls": len(deskmap["controls"]),
        "enabled": sum(1 for c in deskmap["controls"].values() if c["enabled"]),
        "dials": len(deskmap["dials"]),
        "pages": [page["key"] for page in deskmap["pages"]],
    }
