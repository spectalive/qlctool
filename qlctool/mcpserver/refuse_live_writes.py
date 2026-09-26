"""The guard in front of every tool that changes what a running QLC+ is doing."""

from .mcp_message import mcp_message
from .mcp_settings import McpSettings


def refuse_live_writes(settings: McpSettings, tool: str) -> None:
    """Raise, naming `--allow-live-writes`, unless the server was started with it."""
    if not settings.allow_writes:
        raise PermissionError(mcp_message("mcp_live_writes_off", tool=tool))
