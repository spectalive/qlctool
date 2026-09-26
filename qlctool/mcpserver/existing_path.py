"""A path a tool reads, resolved, and refused when it is not there."""

from pathlib import Path

from .mcp_message import mcp_message


def existing_path(path: str) -> Path:
    """`path` made absolute; a ValueError naming it when nothing is there."""
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise ValueError(mcp_message("mcp_path_missing", path=resolved))
    return resolved
