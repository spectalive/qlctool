"""The `live_status` tool: is a QLC+ running there, and is it running this workspace."""

from typing import Any

from ..workspace import Workspace
from .existing_path import existing_path
from .id_name_pairs import id_name_pairs
from .mcp_settings import McpSettings
from .qlc_link import QlcLink
from .workspace_functions import workspace_functions


def live_status(settings: McpSettings, workspace: str | None = None) -> dict[str, Any]:
    """Reachability, and the running show's size; with `workspace`, whether it is that file.

    QLC+'s web API does not say which file it loaded, so the running show is
    compared with the workspace function by function: same ids, same names.
    """
    try:
        with QlcLink(settings) as link:
            loaded = link.ask("isProjectLoaded")
            functions = dict(id_name_pairs(link.ask("getFunctionsList")))
            widgets = id_name_pairs(link.ask("getWidgetsList"))
    except ConnectionError as error:
        return {"reachable": False, "url": settings.url, "error": str(error)}
    status: dict[str, Any] = {
        "reachable": True,
        "url": settings.url,
        "project_loaded": loaded[0] == "true",
        "functions": len(functions),
        "widgets": len(widgets),
        "writes_allowed": settings.allow_writes,
    }
    if workspace is not None:
        path = existing_path(workspace)
        saved = workspace_functions(Workspace.load(path).root)
        status["workspace"] = {
            "path": str(path),
            "matches": saved == functions,
            "only_in_file": len(saved.keys() - functions.keys()),
            "only_running": len(functions.keys() - saved.keys()),
            "renamed": sum(
                1 for fid in saved.keys() & functions.keys() if saved[fid] != functions[fid]
            ),
        }
    return status
