"""Which packages of the optional `mcp` extra this environment lacks."""

import importlib

MCP_EXTRA = ("mcp", "websockets")


def missing_mcp_extra() -> list[str]:
    """The extra's packages that do not import; empty when `qlctool[mcp]` is installed."""
    missing = []
    for name in MCP_EXTRA:
        try:
            importlib.import_module(name)
        except ImportError:
            missing.append(name)
    return missing
