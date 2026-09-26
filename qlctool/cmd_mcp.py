"""`qlctool mcp`: serve the toolkit to an agent over MCP's stdio transport."""

import argparse
import sys

from .mcpserver.mcp_message import mcp_message
from .mcpserver.mcp_settings import McpSettings
from .missing_mcp_extra import missing_mcp_extra


def cmd_mcp(args: argparse.Namespace) -> int:
    """Run the server until the client closes stdin; exit 1 when the extra is not installed."""
    missing = missing_mcp_extra()
    if missing:
        print(
            f"qlctool: {mcp_message('mcp_extra_missing', missing=', '.join(missing))}",
            file=sys.stderr,
        )
        return 1
    # Imported here: plain qlctool never loads the MCP SDK or the websocket client.
    from .mcpserver.build_server import build_server

    settings = McpSettings(
        host=args.qlc_host,
        port=args.qlc_port,
        allow_writes=args.allow_live_writes,
        fixtures=tuple(args.fixtures or ()),
    )
    build_server(settings).run("stdio")
    return 0
