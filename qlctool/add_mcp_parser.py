"""The `qlctool mcp` subcommand's arguments."""

import argparse

from .cmd_mcp import cmd_mcp

SUMMARY = (
    "serve build, check, validate and live QLC+ tools to an agent over MCP (stdio); "
    "needs the optional qlctool[mcp] extra (docs/mcp.md)"
)


def add_mcp_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    parser = sub.add_parser("mcp", help=SUMMARY, description=SUMMARY)
    parser.add_argument(
        "--qlc-host", default="127.0.0.1", help="host of the running QLC+ (default 127.0.0.1)"
    )
    parser.add_argument(
        "--qlc-port", type=int, default=9999, help="its web API port, QLC+'s --wp (default 9999)"
    )
    parser.add_argument(
        "--allow-live-writes",
        action="store_true",
        help="let live_press and live_function change the running show (default: read only)",
    )
    parser.set_defaults(func=cmd_mcp)
