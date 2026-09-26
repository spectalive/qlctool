"""The `live_functions` tool: the running show's functions."""

from typing import Any

from .id_name_pairs import id_name_pairs
from .mcp_settings import McpSettings
from .qlc_link import QlcLink


def live_functions(settings: McpSettings, detail: bool = False) -> list[dict[str, Any]]:
    """Every function's id and name; with `detail`, its type and whether it is running."""
    with QlcLink(settings) as link:
        functions = [
            {"id": fid, "name": name} for fid, name in id_name_pairs(link.ask("getFunctionsList"))
        ]
        if detail:
            for function in functions:
                function["type"] = link.ask("getFunctionType", function["id"])[0]
                function["running"] = link.ask("getFunctionStatus", function["id"])[0] == "Running"
    return functions
