"""Read one `qlctool.toml`, refusing keys it does not know."""

import tomllib
from pathlib import Path

from .toolkit_config import ToolkitConfig


def read_toolkit_config(path: Path) -> ToolkitConfig:
    """Every listed folder resolved against the file's own folder."""
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    keys = ("fixtures", "input_profiles", "gobos")
    # Checked here rather than with description/reading/reject_unknown_keys:
    # library.py imports this module, and the description package imports the library.
    unknown = sorted(set(document) - set(keys))
    if unknown:
        raise ValueError(f"{path}: unknown key(s) {', '.join(unknown)}; allowed: {', '.join(keys)}")
    folders: dict[str, tuple[Path, ...]] = {}
    for key in keys:
        entries = document.get(key, [])
        if not isinstance(entries, list) or not all(isinstance(e, str) and e for e in entries):
            raise ValueError(f"{path}: {key} must be a list of folder names")
        folders[key] = tuple(path.parent / entry for entry in entries)
    return ToolkitConfig(**folders)
