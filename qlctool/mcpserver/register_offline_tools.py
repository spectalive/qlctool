"""The tools that work on files: nothing here talks to a running QLC+."""

from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from .mcp_settings import McpSettings
from .tool_check import tool_check
from .tool_deskmap import tool_deskmap
from .tool_errors import tool_errors
from .tool_info import tool_info
from .tool_newshow import tool_newshow
from .tool_pad_palette import tool_pad_palette
from .tool_validate import tool_validate

READS = ToolAnnotations(read_only_hint=True, open_world_hint=False)
# overwrite=true replaces a file, so a write is destructive.
WRITES_A_FILE = ToolAnnotations(read_only_hint=False, destructive_hint=True, open_world_hint=False)
# Starts and stops a QLC+ of its own: not read-only, and outside this process.
RUNS_QLCPLUS = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=True)
# newshow writes a file and, with validate=true, runs QLC+ too.
BUILDS = ToolAnnotations(read_only_hint=False, destructive_hint=True, open_world_hint=True)


def register_offline_tools(server: MCPServer, settings: McpSettings) -> None:
    """Add info, newshow, check, validate, deskmap and pad_palette to `server`."""
    default = list(settings.fixtures) or None

    @server.tool(name="info", annotations=READS)
    def info(workspace: str) -> dict[str, Any]:
        """List a workspace's patched fixtures with their roles, and its fixture groups."""
        with tool_errors():
            return tool_info(workspace, default)

    @server.tool(name="newshow", annotations=BUILDS)
    def newshow(
        out: str,
        workspace: str | None = None,
        description: str | None = None,
        overwrite: bool = False,
        buttons: bool = True,
        validate: bool = False,
    ) -> dict[str, Any]:
        """Build a fresh show on a workspace's patch (or a description's [rig]) and write it to out.

        out must not exist unless overwrite is true. validate loads the result in headless QLC+.
        """
        with tool_errors():
            return tool_newshow(out, workspace, description, overwrite, buttons, validate, default)

    @server.tool(name="check", annotations=READS)
    def check(workspace: str, description: str | None = None, limit: int = 200) -> dict[str, Any]:
        """Check what the show will do in the room; findings worst first, with rule id and severity."""
        with tool_errors():
            return tool_check(workspace, description, limit, default)

    @server.tool(name="validate", annotations=RUNS_QLCPLUS)
    def validate(workspace: str) -> dict[str, Any]:
        """Load an I/O-free copy of a workspace in a QLC+ of the server's own; report its complaints."""
        with tool_errors():
            return tool_validate(workspace)

    @server.tool(name="deskmap", annotations=WRITES_A_FILE)
    def deskmap(
        workspace: str,
        description: str | None = None,
        out: str | None = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """The tablet desk's map of a saved show; with out, written there (never over a file unless overwrite)."""
        with tool_errors():
            return tool_deskmap(workspace, description, out, overwrite, default)

    @server.tool(name="pad_palette", annotations=WRITES_A_FILE)
    def pad_palette(
        workspace: str, out: str | None = None, overwrite: bool = False
    ) -> dict[str, Any]:
        """The SMC-PAD LED bridge's palette of a saved show; with out, written there."""
        with tool_errors():
            return tool_pad_palette(workspace, out, overwrite)
