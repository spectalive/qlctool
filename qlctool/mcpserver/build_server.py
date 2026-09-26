"""The MCP server `qlctool mcp` runs over stdio."""

from importlib.metadata import version

from mcp.server import MCPServer

from .mcp_settings import McpSettings
from .register_live_tools import register_live_tools
from .register_offline_tools import register_offline_tools

INSTRUCTIONS = (
    "Design, check and run QLC+ lighting shows. The offline tools (info, newshow, check, "
    "validate, deskmap, pad_palette) work on workspace files. The live_* tools read a running "
    "QLC+ through its web API; live_press and live_function change what it is doing and refuse "
    "unless the server was started with --allow-live-writes. No tool loads, saves or replaces "
    "the workspace of a running QLC+."
)


def build_server(settings: McpSettings) -> MCPServer:
    """A server with every tool registered, talking to the QLC+ `settings` names."""
    server = MCPServer("qlctool", instructions=INSTRUCTIONS, version=version("qlctool"))
    register_offline_tools(server, settings)
    register_live_tools(server, settings)
    return server
