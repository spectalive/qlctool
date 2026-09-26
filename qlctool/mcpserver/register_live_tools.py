"""The tools that talk to a running QLC+ through its web API websocket."""

from typing import Any, Literal

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from .live_channels import live_channels
from .live_function import live_function
from .live_functions import live_functions
from .live_press import live_press
from .live_status import live_status
from .live_widgets import live_widgets
from .mcp_settings import McpSettings
from .tool_errors import tool_errors

READS = ToolAnnotations(read_only_hint=True, open_world_hint=True)
DRIVES = ToolAnnotations(read_only_hint=False, destructive_hint=True, open_world_hint=True)


def register_live_tools(server: MCPServer, settings: McpSettings) -> None:
    """Add the live reads, and the two writes that refuse unless `--allow-live-writes` was given."""

    @server.tool(name="live_status", annotations=READS)
    def status(workspace: str | None = None) -> dict[str, Any]:
        """Is a QLC+ web API reachable, how big is its show, and (with workspace) is it that file."""
        with tool_errors():
            return live_status(settings, workspace)

    @server.tool(name="live_widgets", annotations=READS)
    def widgets(detail: bool = True) -> list[dict[str, Any]]:
        """The running virtual console's widgets: id, caption, and with detail type, state and function."""
        with tool_errors():
            return live_widgets(settings, detail)

    @server.tool(name="live_functions", annotations=READS)
    def functions(detail: bool = False) -> list[dict[str, Any]]:
        """The running show's functions: id and name, and with detail type and running."""
        with tool_errors():
            return live_functions(settings, detail)

    @server.tool(name="live_channels", annotations=READS)
    def channels(universe: int = 1, start: int = 1, count: int = 16) -> list[dict[str, Any]]:
        """DMX values of count channels from start (1-based) in universe (1-based), before the grand master."""
        with tool_errors():
            return live_channels(settings, universe, start, count)

    @server.tool(name="live_press", annotations=DRIVES)
    def press(widget_id: int, value: int = 255) -> dict[str, Any]:
        """Press (255) or release (0) a console widget, or set a slider; needs --allow-live-writes."""
        with tool_errors():
            return live_press(settings, widget_id, value)

    @server.tool(name="live_function", annotations=DRIVES)
    def function(function_id: int, state: Literal["on", "off"]) -> dict[str, Any]:
        """Start (on) or stop (off) a function directly, past the console; needs --allow-live-writes."""
        with tool_errors():
            return live_function(settings, function_id, state)
