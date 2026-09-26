"""The `live_function` tool: start or stop a function of the running show."""

import time
from typing import Any, Literal

from .mcp_message import mcp_message
from .mcp_settings import McpSettings
from .qlc_link import QlcLink
from .refuse_live_writes import refuse_live_writes
from .settle_seconds import SETTLE_SECONDS

# `Function::typeToString(Undefined)`: a constant, not translated.
UNDEFINED = "Undefined"


def live_function(
    settings: McpSettings, function_id: int, state: Literal["on", "off"]
) -> dict[str, Any]:
    """`QLC+API|setFunctionStatus|<id>|1` or `|0`, and whether it is running afterwards.

    The function is asked its type first, so an id the show lacks is refused
    before anything is sent. This starts the function itself, past the
    console: no button lights and no solo frame stops its neighbours. Refused
    unless the server was started with `--allow-live-writes`.
    """
    refuse_live_writes(settings, "live_function")
    with QlcLink(settings) as link:
        kind = link.ask("getFunctionType", function_id)[0]
        if kind == UNDEFINED:
            raise ValueError(mcp_message("mcp_live_no_function", function=function_id))
        link.send(f"QLC+API|setFunctionStatus|{function_id}|{1 if state == 'on' else 0}")
        time.sleep(SETTLE_SECONDS)
        running = link.ask("getFunctionStatus", function_id)[0] == "Running"
    return {"function": function_id, "type": kind, "running": running}
