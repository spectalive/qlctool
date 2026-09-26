"""The `live_function` tool: start or stop a function of the running show."""

import time
from typing import Any, Literal

from .id_name_pairs import id_name_pairs
from .mcp_message import mcp_message
from .mcp_settings import McpSettings
from .qlc_link import QlcLink
from .refuse_live_writes import refuse_live_writes
from .settle_seconds import SETTLE_SECONDS


def live_function(
    settings: McpSettings, function_id: int, state: Literal["on", "off"]
) -> dict[str, Any]:
    """`QLC+API|setFunctionStatus|<id>|1` or `|0`, and whether it is running afterwards.

    This starts the function itself, past the console: no button lights and
    no solo frame stops its neighbours. Refused unless the server was started
    with `--allow-live-writes`.
    """
    refuse_live_writes(settings, "live_function")
    with QlcLink(settings) as link:
        functions = dict(id_name_pairs(link.ask("getFunctionsList")))
        if function_id not in functions:
            raise ValueError(mcp_message("mcp_live_no_function", function=function_id))
        link.send(f"QLC+API|setFunctionStatus|{function_id}|{1 if state == 'on' else 0}")
        time.sleep(SETTLE_SECONDS)
        running = link.ask("getFunctionStatus", function_id)[0] == "Running"
    return {"function": function_id, "name": functions[function_id], "running": running}
