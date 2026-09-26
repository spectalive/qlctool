"""The `pad_palette` tool: the SMC-PAD LED bridge's palette of a saved show."""

import json
from typing import Any

from ..build_pad_palette import build_pad_palette
from ..workspace import Workspace
from .existing_path import existing_path
from .output_path import output_path


def tool_pad_palette(
    workspace: str, out: str | None = None, overwrite: bool = False
) -> dict[str, Any]:
    """The palette `qlctool pad-palette` writes; with `out`, written there as the CLI does."""
    path = existing_path(workspace)
    palette = build_pad_palette(Workspace.load(path), path)
    if out is None:
        return palette
    target = output_path(out, overwrite)
    text = json.dumps(palette, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    target.write_text(text, encoding="utf-8")
    lit = sum(1 for pad in palette["pads"] if pad["lit"])
    return {"out": str(target), "pads": len(palette["pads"]), "lit": lit}
