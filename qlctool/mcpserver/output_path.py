"""A path a tool writes, resolved and checked before anything is written."""

from pathlib import Path

import qlctool

from .mcp_message import mcp_message

PACKAGE_DIR = Path(qlctool.__file__).resolve().parent


def output_path(path: str, overwrite: bool) -> Path:
    """`path` made absolute, or a ValueError.

    Refused: a folder that does not exist, anything inside the installed
    package, and an existing file unless `overwrite` says to replace it.
    """
    resolved = Path(path).expanduser().resolve()
    if not resolved.parent.is_dir():
        raise ValueError(mcp_message("mcp_output_folder_missing", path=resolved))
    if resolved.is_relative_to(PACKAGE_DIR):
        raise ValueError(mcp_message("mcp_output_in_package", path=resolved))
    if resolved.exists() and not overwrite:
        raise ValueError(mcp_message("mcp_output_exists", path=resolved))
    return resolved
