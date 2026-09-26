"""The `validate` tool: does a real QLC+ load the file without complaint."""

from typing import Any

from ..validate import validate_workspace
from .existing_path import existing_path


def tool_validate(workspace: str) -> dict[str, Any]:
    """Load the workspace in a QLC+ of this tool's own, headless, and return its complaints.

    A QLC+ somebody already has open stays open; with no QLC+
    installed this fails rather than pass.
    """
    path = existing_path(workspace)
    result = validate_workspace(path)
    return {"workspace": str(path), "ok": result.ok, "errors": list(result.errors)}
