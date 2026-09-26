"""The refusals and failures an agent should read, passed to it instead of hidden.

The MCP SDK keeps the text of an unexpected exception on the server and tells
the client only "Error executing tool" (mcp 2.x, `Tool.run`); only a
`ToolError` reaches the model. A path that is not there, an output that would
replace a file, a write the server was not allowed, a QLC+ that does not
answer: each is the answer the agent needs, so each becomes a `ToolError`.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from mcp.server.mcpserver.exceptions import ToolError

# OSError covers PermissionError (a live write refused), ConnectionError (no
# QLC+ there), TimeoutError and FileNotFoundError (no QLC+ installed);
# RuntimeError is a QLC+ that ran and logged nothing; ValueError also covers
# a description or a name the catalogues refuse.
TOLD = (ValueError, OSError, RuntimeError)


@contextmanager
def tool_errors() -> Iterator[None]:
    """Re-raise the expected failures of the block as a `ToolError` with the same text."""
    try:
        yield
    except TOLD as error:
        raise ToolError(str(error)) from error
