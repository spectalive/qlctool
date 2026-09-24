"""The config governing a path, or an empty one when there is none."""

from pathlib import Path

from .find_toolkit_config import find_toolkit_config
from .read_toolkit_config import read_toolkit_config
from .toolkit_config import ToolkitConfig


def toolkit_config_from(start: Path) -> ToolkitConfig:
    """Nearest `qlctool.toml` at or above `start`, read; `ToolkitConfig()` otherwise."""
    found = find_toolkit_config(start)
    return read_toolkit_config(found) if found is not None else ToolkitConfig()
