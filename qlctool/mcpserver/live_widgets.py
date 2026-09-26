"""The `live_widgets` tool: the running virtual console, widget by widget."""

from typing import Any

from .id_name_pairs import id_name_pairs
from .mcp_settings import McpSettings
from .qlc_link import QlcLink


def live_widgets(settings: McpSettings, detail: bool = True) -> list[dict[str, Any]]:
    """Every widget's id and caption; with `detail`, its type, state and function.

    The state is QLC+'s own: a button answers 255 active, 127 monitoring, 0
    off; a slider its value; a cue list `PLAY|<step>` or `STOP`.
    """
    with QlcLink(settings) as link:
        widgets = [
            {"id": wid, "caption": caption}
            for wid, caption in id_name_pairs(link.ask("getWidgetsList"))
        ]
        if not detail:
            return widgets
        for widget in widgets:
            widget["type"] = link.ask("getWidgetType", widget["id"])[-1]
            widget["state"] = "|".join(link.ask("getWidgetStatus", widget["id"])[1:])
            function = link.ask("getWidgetFunction", widget["id"])
            widget["function"] = int(function[1]) if function[1] != "0" else None
            widget["function_name"] = function[3] if function[1] != "0" else None
    return widgets
